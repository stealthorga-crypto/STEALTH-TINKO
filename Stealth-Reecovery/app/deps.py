from typing import Generator, List, Optional
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .db import SessionLocal
from .security import decode_jwt
from .models import User, Organization

security = HTTPBearer(auto_error=False)  # Allow missing auth header in dev mode


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    In development mode without auth, returns a mock user.
    """
    # Development mode bypass
    if os.getenv('ENVIRONMENT', 'development') == 'development' and not credentials:
        # Return a mock user for development (not attached to session)
        from types import SimpleNamespace
        
        mock_org = SimpleNamespace(
            id=1,
            name="Dev Organization",
            slug="dev-org",
            is_active=True
        )
        
        mock_user = SimpleNamespace(
            id=1,
            email="dev@example.com",
            full_name="Dev User",
            org_id=1,
            role="admin",
            is_active=True,
            organization=mock_org
        )
        
        return mock_user
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = decode_jwt(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    return user


def require_roles(allowed_roles: List[str]):
    """
    Dependency factory to require specific roles.
    
    Usage:
        @app.get("/admin")
        def admin_route(user: User = Depends(require_roles(["admin"]))):
            ...
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {allowed_roles}",
            )
        return current_user
    return role_checker


def get_current_org(current_user: User = Depends(get_current_user)) -> Organization:
    """
    Dependency to get the current user's organization.
    """
    return current_user.organization
