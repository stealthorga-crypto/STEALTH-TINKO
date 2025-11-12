"""
Authentication Service for STEALTH-TINKO
Handles Gmail OAuth, Mobile OTP, and user registration
"""
import httpx
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from fastapi import HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.db import get_db
from app.models import User, MobileOTP, UserSession, OTPSecurityLog
from app.schemas.auth import (
    UserCreate, UserResponse, GoogleLoginRequest, MobileLoginRequest,
    VerifyOTPRequest, TokenResponse, OTPResponse, GoogleUserInfo
)
from app.security import (
    create_access_token, create_refresh_token, verify_password, 
    get_password_hash, verify_token
)
from app.config import settings
from app.services.sms_service import send_otp_sms, verify_otp_sms
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Comprehensive authentication service"""
    
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        
    async def register_user(self, user_data: UserCreate, request: Request) -> UserResponse:
        """Register new user with email and/or mobile verification"""
        try:
            # Validate user data
            if not user_data.email and not user_data.mobile_number:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Either email or mobile number is required"
                )
            
            # Check if user already exists
            existing_user = None
            if user_data.email:
                existing_user = self.db.query(User).filter(User.email == user_data.email).first()
            if not existing_user and user_data.mobile_number:
                existing_user = self.db.query(User).filter(
                    User.mobile_number == user_data.mobile_number
                ).first()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already exists with this email or mobile number"
                )
            
            # Determine auth provider
            if user_data.mobile_number and not user_data.password:
                auth_provider = "mobile_otp"
            else:
                auth_provider = "email"
            
            # Hash password if provided
            hashed_password = None
            if user_data.password:
                hashed_password = get_password_hash(user_data.password)
            
            # Create new user
            user = User(
                email=user_data.email,
                mobile_number=user_data.mobile_number,
                full_name=user_data.full_name,
                hashed_password=hashed_password,
                country_code=user_data.country_code,
                auth_provider=auth_provider,
                account_type="customer",  # Default for new registrations
                is_active=True,
                preferred_language=user_data.preferred_language or "en",
                timezone=user_data.timezone or "UTC",
                auth_providers=[auth_provider]
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"New user registered: {user.id}, auth_provider: {auth_provider}")
            
            # Send verification based on auth method
            if user_data.mobile_number:
                await self.send_mobile_otp(user_data.mobile_number, request)
            
            return UserResponse.from_orm(user)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"User registration failed: {str(e)}")
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed"
            )
    
    async def google_oauth_login(self, request: GoogleLoginRequest) -> TokenResponse:
        """Handle Google OAuth login"""
        try:
            # Verify Google token and get user info
            user_info = await self._verify_google_token(request.access_token)
            
            # Check if user exists
            user = self.db.query(User).filter(
                or_(
                    User.google_id == user_info.sub,
                    User.email == user_info.email
                )
            ).first()
            
            if user:
                # Update existing user with Google data
                if not user.google_id:
                    user.google_id = user_info.sub
                user.google_email = user_info.email
                user.avatar_url = user_info.picture
                user.is_email_verified = user_info.email_verified
                user.last_login = datetime.utcnow()
                user.login_count += 1
                
                # Add google to auth providers if not present
                if "google" not in user.auth_providers:
                    auth_providers = user.auth_providers or []
                    auth_providers.append("google")
                    user.auth_providers = auth_providers
                
                self.db.commit()
                
            else:
                # Create new user from Google data
                user = User(
                    email=user_info.email,
                    google_email=user_info.email,
                    full_name=user_info.name,
                    google_id=user_info.sub,
                    avatar_url=user_info.picture,
                    auth_provider="google",
                    auth_providers=["google"],
                    account_type="customer",
                    is_active=True,
                    is_email_verified=user_info.email_verified,
                    email_verified_at=datetime.utcnow() if user_info.email_verified else None,
                    last_login=datetime.utcnow(),
                    login_count=1
                )
                
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)
                
                logger.info(f"New Google user created: {user.id}")
            
            # Generate tokens
            access_token = create_access_token(
                data={"sub": str(user.id), "email": user.email, "auth_provider": "google"}
            )
            refresh_token = create_refresh_token(data={"sub": str(user.id)})
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=UserResponse.from_orm(user)
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Google OAuth login failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google authentication failed"
            )
    
    async def send_mobile_otp(self, mobile_number: str, request: Request) -> OTPResponse:
        """Send OTP to mobile number using Twilio Verify Service"""
        try:
            ip_address = request.client.host
            
            # Rate limiting check
            await self._check_otp_rate_limit(mobile_number, ip_address)
            
            # Send OTP via enhanced SMS service (Twilio Verify or fallback)
            sms_result = await send_otp_sms(mobile_number, template_type="signup")
            
            if not sms_result["success"]:
                logger.error(f"SMS service failed for {mobile_number}: {sms_result.get('error')}")
                # Continue with database logging even if SMS fails
            
            # For Twilio Verify, we don't generate our own OTP
            # For basic SMS or development mode, we may get an OTP code back
            otp_code = sms_result.get("otp_code", "******")  # Mask for logging
            
            # Set expiration time (5 minutes)
            expires_at = datetime.utcnow() + timedelta(minutes=5)
            
            # Invalidate previous OTPs for this mobile number
            self.db.query(MobileOTP).filter(
                and_(
                    MobileOTP.mobile_number == mobile_number,
                    MobileOTP.is_used == False
                )
            ).update({"is_used": True})
            
            # Create new OTP record (for tracking purposes)
            mobile_otp = MobileOTP(
                mobile_number=mobile_number,
                otp_code="VERIFY" if sms_result.get("provider") == "twilio_verify" else otp_code,
                expires_at=expires_at,
                ip_address=ip_address,
                user_agent=request.headers.get("user-agent", "")
            )
            
            self.db.add(mobile_otp)
            
            # Log security event
            security_log = OTPSecurityLog(
                email=mobile_number,  # Using email field for mobile too
                ip_address=ip_address,
                user_agent=request.headers.get("user-agent", ""),
                action="request_otp",
                success=sms_result["success"]
            )
            self.db.add(security_log)
            
            self.db.commit()
            
            logger.info(f"OTP sent to {mobile_number} via {sms_result.get('provider', 'unknown')}")
            
            return OTPResponse(
                message=sms_result.get("message", "OTP sent successfully"),
                expires_in=300,
                mobile_number=mobile_number,
                can_resend_after=60
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Send OTP failed for {mobile_number}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send OTP"
            )
    
    async def verify_mobile_otp(self, request: VerifyOTPRequest, req: Request) -> TokenResponse:
        """Verify OTP using Twilio Verify Service or fallback verification"""
        try:
            ip_address = req.client.host
            
            # First try Twilio Verify Service verification
            verify_result = await verify_otp_sms(request.mobile_number, request.otp)
            
            if verify_result["success"] and verify_result.get("valid"):
                # Twilio Verify succeeded
                logger.info(f"OTP verified via {verify_result.get('provider')} for {request.mobile_number}")
                verification_method = verify_result.get('provider', 'twilio_verify')
            else:
                # Fallback to database verification for development/legacy
                logger.info(f"Twilio Verify result: {verify_result}, checking database fallback")
                
                # Find valid OTP in database
                otp_record = self.db.query(MobileOTP).filter(
                    and_(
                        MobileOTP.mobile_number == request.mobile_number,
                        MobileOTP.otp_code == request.otp,
                        MobileOTP.is_used == False
                    )
                ).first()
                
                if not otp_record:
                    # Log failed attempt
                    security_log = OTPSecurityLog(
                        email=request.mobile_number,
                        ip_address=ip_address,
                        user_agent=req.headers.get("user-agent", ""),
                        action="verify_otp",
                        success=False
                    )
                    self.db.add(security_log)
                    self.db.commit()
                    
                    error_detail = "Invalid or expired OTP"
                    if verify_result.get("message"):
                        error_detail = verify_result["message"]
                    
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=error_detail
                    )
                
                # Check if OTP is expired
                if otp_record.is_expired():
                    otp_record.is_used = True
                    self.db.commit()
                    
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="OTP has expired"
                    )
                
                # Check attempt count
                otp_record.attempts += 1
                if otp_record.attempts > 3:
                    otp_record.is_used = True
                    self.db.commit()
                    
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Too many invalid attempts"
                    )
                
                # Mark OTP as used
                otp_record.is_used = True
                verification_method = "database_fallback"
            
            # Find or create user
            user = self.db.query(User).filter(
                User.mobile_number == request.mobile_number
            ).first()
            
            if user:
                # Update existing user
                user.mobile_verified = True
                user.mobile_verified_at = datetime.utcnow()
                user.last_login = datetime.utcnow()
                user.login_count += 1
            else:
                # Create new user
                user = User(
                    mobile_number=request.mobile_number,
                    auth_provider="mobile_otp",
                    auth_providers=["mobile_otp"],
                    account_type="customer",
                    is_active=True,
                    mobile_verified=True,
                    mobile_verified_at=datetime.utcnow(),
                    last_login=datetime.utcnow(),
                    login_count=1
                )
                self.db.add(user)
            
            # Log successful verification
            security_log = OTPSecurityLog(
                email=request.mobile_number,
                ip_address=ip_address,
                user_agent=req.headers.get("user-agent", ""),
                action="verify_otp",
                success=True
            )
            self.db.add(security_log)
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"OTP verified successfully for user {user.id} via {verification_method}")
            
            # Generate tokens
            access_token = create_access_token(
                data={"sub": str(user.id), "mobile": user.mobile_number, "auth_provider": "mobile_otp"}
            )
            refresh_token = create_refresh_token(data={"sub": str(user.id)})
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=UserResponse.from_orm(user)
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"OTP verification failed: {str(e)}")
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OTP verification failed"
            )
    
    async def email_password_login(self, email: str, password: str, request: Request) -> TokenResponse:
        """Traditional email/password login"""
        try:
            # Find user by email
            user = self.db.query(User).filter(
                and_(User.email == email, User.is_active == True)
            ).first()
            
            if not user or not verify_password(password, user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Update login info
            user.last_login = datetime.utcnow()
            user.login_count += 1
            self.db.commit()
            
            # Generate tokens
            access_token = create_access_token(
                data={"sub": str(user.id), "email": user.email, "auth_provider": "email"}
            )
            refresh_token = create_refresh_token(data={"sub": str(user.id)})
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=UserResponse.from_orm(user)
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Email login failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed"
            )
    
    # Private helper methods
    async def _verify_google_token(self, access_token: str) -> GoogleUserInfo:
        """Verify Google OAuth token and return user info"""
        async with httpx.AsyncClient() as client:
            # Get user info from Google
            response = await client.get(
                f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}"
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google token"
                )
            
            user_data = response.json()
            return GoogleUserInfo(**user_data)
    
    async def _send_sms(self, phone: str, message: str) -> Dict[str, Any]:
        """Send SMS via Twilio"""
        try:
            # Import Twilio here to avoid dependency issues
            from twilio.rest import Client
            
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            message_obj = client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone
            )
            
            return {
                "status": "sent",
                "sid": message_obj.sid,
                "provider": "twilio"
            }
            
        except Exception as e:
            logger.error(f"SMS sending failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send SMS: {str(e)}"
            )
    
    def _generate_otp(self) -> str:
        """Generate secure 6-digit OTP"""
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    
    async def _check_otp_rate_limit(self, mobile_number: str, ip_address: str) -> None:
        """Check OTP rate limiting"""
        now = datetime.utcnow()
        
        # Check mobile number rate limit (max 3 OTPs per hour)
        recent_otps = self.db.query(MobileOTP).filter(
            and_(
                MobileOTP.mobile_number == mobile_number,
                MobileOTP.created_at > now - timedelta(hours=1)
            )
        ).count()
        
        if recent_otps >= 3:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many OTP requests. Please try again later."
            )
        
        # Check IP address rate limit (max 10 OTPs per hour)
        recent_ip_otps = self.db.query(MobileOTP).filter(
            and_(
                MobileOTP.ip_address == ip_address,
                MobileOTP.created_at > now - timedelta(hours=1)
            )
        ).count()
        
        if recent_ip_otps >= 10:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(
            and_(User.id == user_id, User.is_active == True)
        ).first()
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token"""
        try:
            payload = verify_token(refresh_token)
            user_id = int(payload.get("sub"))
            
            user = await self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            # Generate new tokens
            access_token = create_access_token(
                data={"sub": str(user.id), "email": user.email}
            )
            new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=UserResponse.from_orm(user)
            )
            
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )


# Dependency to get AuthService
def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)