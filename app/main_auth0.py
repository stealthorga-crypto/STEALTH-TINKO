"""
FastAPI Application with Auth0 JWT Authentication
Example showing public and protected routes
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import os

# Import Auth0 authentication
from .auth0_auth import get_current_user, require_scope

app = FastAPI(
    title="Tinko API with Auth0",
    description="Protected API using Auth0 RS256 JWT tokens",
    version="2.0.0"
)

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Public Routes
@app.get("/")
async def root():
    """Public endpoint - no authentication required"""
    return {
        "message": "Welcome to Tinko API with Auth0",
        "status": "healthy",
        "auth": "Auth0 RS256 JWT"
    }


@app.get("/healthz")
async def health_check():
    """Health check endpoint - no authentication required"""
    return {
        "status": "ok",
        "auth0_domain": os.getenv("AUTH0_DOMAIN"),
        "auth0_issuer": os.getenv("AUTH0_ISSUER"),
    }


# Protected Routes
@app.get("/private")
async def private_route(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Protected endpoint - requires valid Auth0 JWT token
    
    Example:
        curl -H "Authorization: Bearer <token>" http://localhost:8010/private
    """
    return {
        "message": "This is a protected route",
        "user": {
            "sub": user.get("sub"),
            "email": user.get("email"),
            "name": user.get("name"),
            "scopes": user.get("scope", "").split() if user.get("scope") else [],
            "permissions": user.get("permissions", []),
        }
    }


@app.get("/me")
async def get_user_info(user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information from JWT token"""
    return {
        "user": user
    }


@app.get("/admin")
async def admin_route(user: Dict[str, Any] = Depends(require_scope("admin:access"))):
    """
    Admin-only endpoint - requires 'admin:access' scope
    
    Note: You need to configure this scope in your Auth0 API settings
    """
    return {
        "message": "Admin access granted",
        "user": user.get("sub")
    }


# Example: Data endpoint with authentication
@app.get("/api/data")
async def get_data(user: Dict[str, Any] = Depends(get_current_user)):
    """Example data endpoint requiring authentication"""
    return {
        "data": [
            {"id": 1, "name": "Item 1", "value": 100},
            {"id": 2, "name": "Item 2", "value": 200},
            {"id": 3, "name": "Item 3", "value": 300},
        ],
        "user_id": user.get("sub"),
        "total": 3
    }


# Startup and Shutdown Events
@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    print("=" * 50)
    print("Tinko API with Auth0 Starting...")
    print(f"Auth0 Domain: {os.getenv('AUTH0_DOMAIN')}")
    print(f"Auth0 Issuer: {os.getenv('AUTH0_ISSUER')}")
    print(f"CORS Origins: {CORS_ORIGINS}")
    print("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    print("Tinko API with Auth0 Shutting down...")


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", 8010))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    uvicorn.run(
        "app.main_auth0:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
