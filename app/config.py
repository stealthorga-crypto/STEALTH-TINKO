"""
Configuration settings for STEALTH-TINKO
Handles environment variables and application settings
"""
import os
from typing import Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "STEALTH-TINKO"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/tinko")
    
    # JWT Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-this-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    
    # Twilio SMS
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: Optional[str] = os.getenv("TWILIO_PHONE_NUMBER")
    
    # Redis (for OTP storage)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://stealth-tinko-prod-app-1762804410.azurewebsites.net"
    ]
    
    # Azure settings
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    
    # Email settings (for notifications)
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "noreply@tinko.com")
    
    # Rate limiting
    OTP_RATE_LIMIT_PER_MOBILE: int = 3  # per hour
    OTP_RATE_LIMIT_PER_IP: int = 10     # per hour
    
    # Security
    BCRYPT_ROUNDS: int = 12
    
    @validator("ALLOWED_ORIGINS")
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()


# Environment-specific overrides
if settings.ENVIRONMENT == "development":
    settings.DEBUG = True
    settings.ALLOWED_ORIGINS.extend([
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ])


# Validation
def validate_settings():
    """Validate critical settings"""
    issues = []
    
    if settings.JWT_SECRET_KEY == "change-this-in-production":
        issues.append("JWT_SECRET_KEY must be set in production")
    
    if settings.ENVIRONMENT == "production":
        if not settings.GOOGLE_CLIENT_ID:
            issues.append("GOOGLE_CLIENT_ID must be set for Google OAuth")
        if not settings.TWILIO_ACCOUNT_SID:
            issues.append("TWILIO_ACCOUNT_SID must be set for SMS")
    
    if issues:
        raise ValueError(f"Configuration issues: {', '.join(issues)}")


# Auto-validate on import in production
if settings.ENVIRONMENT == "production":
    validate_settings()