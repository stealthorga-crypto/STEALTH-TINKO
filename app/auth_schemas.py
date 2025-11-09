"""
Authentication schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: Optional[str] = Field(None, min_length=8)  # Optional for OAuth registration
    org_name: Optional[str] = None
    org_slug: Optional[str] = None
    account_type: Optional[str] = Field("user", regex="^(user|customer|admin)$")
    
    # API key details for customers
    api_key_name: Optional[str] = None
    api_scopes: Optional[List[str]] = Field(default=["read"])


class UserCreateWithPassword(UserCreate):
    """For traditional email/password registration"""
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class GoogleOAuthSignup(BaseModel):
    """For Google OAuth with additional customer info"""
    org_name: Optional[str] = None
    org_slug: Optional[str] = None
    account_type: Optional[str] = Field("user", regex="^(user|customer|admin)$")
    api_key_name: Optional[str] = None


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    org_id: int
    account_type: str
    auth_providers: List[str]
    is_email_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ApiKeyResponse(BaseModel):
    id: int
    key_name: str
    key_prefix: str
    scopes: List[str]
    is_active: bool
    last_used_at: Optional[datetime]
    usage_count: int
    expires_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ApiKeyCreate(BaseModel):
    key_name: str = Field(..., min_length=1, max_length=128)
    scopes: List[str] = Field(default=["read"])
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)


class ApiKeyCreateResponse(BaseModel):
    """Response when creating API key - includes the actual key"""
    api_key: str  # The actual key - only shown once
    key_info: ApiKeyResponse


class OrganizationResponse(BaseModel):
    id: int
    name: str
    slug: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    organization: OrganizationResponse


class TokenPayload(BaseModel):
    user_id: int
    org_id: int
    role: str
    exp: int
