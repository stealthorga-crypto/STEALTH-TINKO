"""
Authentication router for user registration and login.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import re

from ..deps import get_db, get_current_user
from ..models import User, Organization
from ..security import hash_password, verify_password, create_jwt
from ..auth_schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    OrganizationResponse,
    TokenResponse,
)

router = APIRouter(prefix="/v1/auth", tags=["auth"])


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user and optionally create a new organization.
    
    If org_name is provided, creates a new organization.
    Otherwise, requires invitation to existing org (not implemented yet).
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create or get organization
    if user_data.org_name:
        # Create new organization
        org_slug = user_data.org_slug or slugify(user_data.org_name)
        
        # Check if slug already exists
        existing_org = db.query(Organization).filter(Organization.slug == org_slug).first()
        if existing_org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Organization slug '{org_slug}' already exists",
            )
        
        organization = Organization(
            name=user_data.org_name,
            slug=org_slug,
            is_active=True,
        )
        db.add(organization)
        db.flush()  # Get the org ID
        
        # First user in new org is admin
        role = "admin"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization name required for new registration",
        )
    
    # Create user
    hashed_pw = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_pw,
        full_name=user_data.full_name,
        role=role,
        org_id=organization.id,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.refresh(organization)
    
    # Create JWT token
    token_data = {
        "user_id": user.id,
        "org_id": user.org_id,
        "role": user.role,
    }
    access_token = create_jwt(token_data)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user),
        organization=OrganizationResponse.from_orm(organization),
    )


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token.
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    # Create JWT token
    token_data = {
        "user_id": user.id,
        "org_id": user.org_id,
        "role": user.role,
    }
    access_token = create_jwt(token_data)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user),
        organization=OrganizationResponse.from_orm(user.organization),
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    """
    return UserResponse.from_orm(current_user)


@router.get("/org", response_model=OrganizationResponse)
def get_current_organization(current_user: User = Depends(get_current_user)):
    """
    Get current user's organization information.
    """
    return OrganizationResponse.from_orm(current_user.organization)
