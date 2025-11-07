"""
Authentication schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    org_name: Optional[str] = None
    org_slug: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    org_id: int
    created_at: datetime

    class Config:
        from_attributes = True


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


# OTP Registration Flow Schemas
class RegisterStartResponse(BaseModel):
    ok: bool = True
    message: str = "OTP sent to email"


class VerifyRequest(BaseModel):
    email: EmailStr
    code: str
    password: str = Field(..., min_length=8)
    full_name: str
    org_name: str
    org_slug: Optional[str] = None


class VerifyResponse(BaseModel):
    ok: bool = True
    message: str = "Email verified. You can now sign in."
