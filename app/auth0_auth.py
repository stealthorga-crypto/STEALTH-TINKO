"""
Auth0 JWT Verification for FastAPI
Validates RS256 JWT tokens from Auth0
"""

import os
from typing import Optional, Dict, Any
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, jwk, JWTError
from jose.utils import base64url_decode
import requests
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

# Auth0 Configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_ISSUER = os.getenv("AUTH0_ISSUER")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE", "")

if not AUTH0_DOMAIN or not AUTH0_ISSUER:
    raise ValueError("AUTH0_DOMAIN and AUTH0_ISSUER environment variables are required")

# HTTP Bearer token security scheme
security = HTTPBearer()

# JWKS cache
_jwks_cache: Optional[Dict[str, Any]] = None


@lru_cache(maxsize=1)
def get_jwks_url() -> str:
    """Get the JWKS URL for the Auth0 tenant"""
    return f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"


def fetch_jwks() -> Dict[str, Any]:
    """
    Fetch the JSON Web Key Set from Auth0
    Cached globally to avoid repeated requests
    """
    global _jwks_cache
    
    if _jwks_cache is not None:
        return _jwks_cache
    
    try:
        jwks_url = get_jwks_url()
        response = requests.get(jwks_url, timeout=10)
        response.raise_for_status()
        _jwks_cache = response.json()
        logger.info(f"Fetched JWKS from {jwks_url}")
        return _jwks_cache
    except Exception as e:
        logger.error(f"Failed to fetch JWKS: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch authentication keys"
        )


def get_signing_key(token: str) -> Optional[str]:
    """
    Get the public key for verifying the JWT signature
    """
    try:
        # Decode the JWT header without verification
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        
        if not kid:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing key ID"
            )
        
        # Get JWKS
        jwks = fetch_jwks()
        
        # Find the key with matching kid
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return jwk.construct(key).to_pem().decode("utf-8")
        
        raise HTTPException(
            status_code=401,
            detail="Invalid token: key not found"
        )
    except JWTError as e:
        logger.error(f"JWT error: {e}")
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode an Auth0 JWT token
    
    Args:
        token: The JWT token string
    
    Returns:
        The decoded token payload
    
    Raises:
        HTTPException: If the token is invalid
    """
    try:
        # Get the signing key
        signing_key = get_signing_key(token)
        
        # Verify and decode the token
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=AUTH0_ISSUER,
            audience=AUTH0_AUDIENCE if AUTH0_AUDIENCE else None,
            options={
                "verify_signature": True,
                "verify_aud": bool(AUTH0_AUDIENCE),
                "verify_iat": True,
                "verify_exp": True,
                "verify_nbf": False,
                "verify_iss": True,
                "verify_sub": True,
                "verify_jti": False,
                "verify_at_hash": False,
                "require_aud": bool(AUTH0_AUDIENCE),
                "require_iat": False,
                "require_exp": True,
                "require_nbf": False,
                "require_iss": True,
                "require_sub": True,
                "require_jti": False,
                "require_at_hash": False,
            }
        )
        
        logger.info(f"Token verified for user: {payload.get('sub')}")
        return payload
    
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except jwt.JWTClaimsError as e:
        logger.warning(f"Invalid token claims: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid token claims"
        )
    except JWTError as e:
        logger.error(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        raise HTTPException(
            status_code=500,
            detail="Authentication error"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency to get the current authenticated user from the token
    
    Usage:
        @app.get("/protected")
        async def protected_route(user: dict = Depends(get_current_user)):
            return {"user": user}
    """
    token = credentials.credentials
    return verify_token(token)


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency to require authentication
    Alias for get_current_user
    """
    return await get_current_user(credentials)


def refresh_jwks_cache():
    """
    Manually refresh the JWKS cache
    Call this periodically or when keys are rotated
    """
    global _jwks_cache
    _jwks_cache = None
    fetch_jwks()
    logger.info("JWKS cache refreshed")


# Optional: Scope-based authorization
def require_scope(required_scope: str):
    """
    Create a dependency that requires a specific scope in the token
    
    Usage:
        @app.get("/admin")
        async def admin_route(user: dict = Depends(require_scope("admin:access"))):
            return {"message": "Admin access granted"}
    """
    async def scope_checker(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        scopes = user.get("scope", "").split()
        permissions = user.get("permissions", [])
        
        if required_scope not in scopes and required_scope not in permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions: '{required_scope}' scope required"
            )
        
        return user
    
    return scope_checker
