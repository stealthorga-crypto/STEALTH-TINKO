from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginOTPRequest(BaseModel):
    """Request model for requesting OTP for login"""
    email: EmailStr
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }

class OTPVerifyRequest(BaseModel):
    """Request model for verifying OTP and completing login"""
    email: EmailStr
    otp_code: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "otp_code": "123456"
            }
        }

class OTPSentResponse(BaseModel):
    """Response model when OTP is successfully sent"""
    message: str
    email: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "OTP sent to your email",
                "email": "user@example.com"
            }
        }

class UserInfo(BaseModel):
    """User information for login response"""
    id: int
    email: str
    # Add other user fields as needed
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com"
            }
        }

class LoginResponse(BaseModel):
    """Response model for successful login with OTP"""
    access_token: str
    token_type: str
    user: UserInfo
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "email": "user@example.com"
                }
            }
        }

class ErrorResponse(BaseModel):
    """Standard error response model"""
    detail: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "User not found. Please sign up first."
            }
        }