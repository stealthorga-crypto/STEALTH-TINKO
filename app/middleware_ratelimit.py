"""
Rate limiting middleware for Auth0 OTP endpoints.

Protects against brute-force attacks by limiting:
- /register/start: Max 5 requests per email per hour
- /register/verify: Max 10 attempts per email per hour
"""

import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import threading

# In-memory rate limit store (use Redis in production)
# Structure: {email: [(timestamp, endpoint), ...]}
_rate_limit_store: Dict[str, list] = defaultdict(list)
_rate_limit_lock = threading.Lock()

# Rate limit config
RATE_LIMITS = {
    "/v1/auth/register/start": {
        "max_requests": 5,
        "window_seconds": 3600,  # 1 hour
    },
    "/v1/auth/register/verify": {
        "max_requests": 10,
        "window_seconds": 3600,  # 1 hour
    },
}


def _clean_old_entries(email: str, window_seconds: int) -> None:
    """Remove entries older than the time window"""
    current_time = time.time()
    cutoff_time = current_time - window_seconds
    
    with _rate_limit_lock:
        if email in _rate_limit_store:
            _rate_limit_store[email] = [
                entry for entry in _rate_limit_store[email]
                if entry[0] > cutoff_time
            ]


def _check_rate_limit(email: str, endpoint: str, max_requests: int, window_seconds: int) -> Tuple[bool, int]:
    """
    Check if request is within rate limit.
    
    Returns:
        (is_allowed, remaining_requests)
    """
    _clean_old_entries(email, window_seconds)
    
    with _rate_limit_lock:
        current_entries = [
            entry for entry in _rate_limit_store[email]
            if entry[1] == endpoint
        ]
        
        if len(current_entries) >= max_requests:
            return False, 0
        
        # Record this request
        _rate_limit_store[email].append((time.time(), endpoint))
        
        remaining = max_requests - len(current_entries) - 1
        return True, remaining


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce rate limits on sensitive endpoints"""
    
    async def dispatch(self, request: Request, call_next):
        # Only apply to configured endpoints
        if request.url.path not in RATE_LIMITS:
            return await call_next(request)
        
        # Get email from request body
        try:
            body = await request.body()
            # Re-add body for downstream processing
            async def receive():
                return {"type": "http.request", "body": body}
            request._receive = receive
            
            # Parse email from JSON body
            import json
            data = json.loads(body.decode())
            email = data.get("email")
            
            if not email:
                return await call_next(request)
            
        except Exception:
            # If we can't parse email, allow the request
            # (it will fail validation later anyway)
            return await call_next(request)
        
        # Check rate limit
        config = RATE_LIMITS[request.url.path]
        is_allowed, remaining = _check_rate_limit(
            email,
            request.url.path,
            config["max_requests"],
            config["window_seconds"]
        )
        
        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
                headers={
                    "Retry-After": str(config["window_seconds"]),
                }
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(config["max_requests"])
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response


def reset_rate_limits() -> None:
    """Reset all rate limits (useful for testing)"""
    global _rate_limit_store
    with _rate_limit_lock:
        _rate_limit_store.clear()
