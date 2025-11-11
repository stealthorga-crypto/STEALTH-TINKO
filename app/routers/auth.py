"""
Authentication router for user registration and login.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional, List
import re
import os
import secrets
import urllib.parse
import httpx

from ..deps import get_db, get_current_user, require_role
from ..models import User, Organization, ApiKey
from ..security import hash_password, verify_password, create_jwt
from ..auth_schemas import (
    UserCreate,
    UserCreateWithPassword,
    UserLogin,
    UserResponse,
    OrganizationResponse,
    TokenResponse,
    GoogleOAuthSignup,
    ApiKeyCreate,
    ApiKeyCreateResponse,
    ApiKeyResponse,
)
# Import enhanced auth service and schemas
from app.services.auth_service import AuthService, get_auth_service
from app.schemas.auth import (
    UserCreate as NewUserCreate, GoogleLoginRequest, MobileLoginRequest,
    VerifyOTPRequest, TokenResponse as NewTokenResponse, OTPResponse, MessageResponse
)

# ========== ENHANCED MOBILE OTP & GOOGLE OAUTH ==========

@router.post("/signup-enhanced", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def signup_enhanced(
    user_data: NewUserCreate,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Enhanced user registration with Gmail OAuth and Mobile OTP support
    
    - **email**: Optional email address (required if no mobile)
    - **mobile_number**: Optional mobile number (required if no email) 
    - **password**: Required for email signup, optional for mobile-only
    - **full_name**: User's full name
    """
    try:
        user = await auth_service.register_user(user_data, request)
        
        # Determine next steps based on auth method
        if user_data.mobile_number and not user_data.password:
            next_step = "verify_mobile_otp"
            message = "User registered. Please verify the OTP sent to your mobile number."
        else:
            next_step = "email_verification"
            message = "User registered successfully. Please check your email for verification."
        
        return MessageResponse(
            message=message,
            success=True,
            details={
                "user_id": user.id,
                "auth_provider": user.auth_provider,
                "next_step": next_step
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/google-oauth", response_model=NewTokenResponse)
async def google_oauth_login(
    request_data: GoogleLoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Enhanced Google OAuth login/registration
    
    - **access_token**: Google OAuth access token from frontend
    """
    return await auth_service.google_oauth_login(request_data)


@router.post("/mobile/send-otp", response_model=OTPResponse)
async def send_mobile_otp(
    otp_request: MobileLoginRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Send OTP to mobile number for login/signup
    
    - **mobile_number**: Mobile number to send OTP
    - **country_code**: Optional country code (defaults to +91)
    """
    # Format mobile number with country code if provided
    mobile_number = otp_request.mobile_number
    if not mobile_number.startswith('+') and otp_request.country_code:
        mobile_number = otp_request.country_code + mobile_number
    
    return await auth_service.send_mobile_otp(mobile_number, request)


@router.post("/mobile/verify-otp", response_model=NewTokenResponse)
async def verify_mobile_otp_enhanced(
    verify_request: VerifyOTPRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Verify OTP and login/register user
    
    - **mobile_number**: Mobile number that received OTP
    - **otp**: 6-digit OTP code
    """
    return await auth_service.verify_mobile_otp(verify_request, request)

router = APIRouter(prefix="/v1/auth", tags=["auth"])


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreateWithPassword, db: Session = Depends(get_db)):
    """
    Register a new user with email/password and optionally create a new organization.
    Can also generate API keys for customers during registration.
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
        account_type=user_data.account_type or "user",
        auth_providers=["email"],
        is_email_verified=False,  # TODO: Add email verification flow
    )
    db.add(user)
    db.flush()  # Get the user ID
    
    # Generate API key if requested (for customers)
    if user_data.api_key_name and user_data.account_type == "customer":
        api_key_plain = ApiKey.generate_key()
        api_key_hash = hash_password(api_key_plain)  # Reuse password hashing
        
        api_key = ApiKey(
            user_id=user.id,
            key_name=user_data.api_key_name,
            key_hash=api_key_hash,
            key_prefix=api_key_plain[:8],  # Store first 8 chars for display
            scopes=user_data.api_scopes or ["read"],
            is_active=True,
        )
        db.add(api_key)
    
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
        user=UserResponse.model_validate(user),
        organization=OrganizationResponse.model_validate(organization),
    )


@router.post("/register/google", response_model=dict)
def register_google_start(signup_data: GoogleOAuthSignup, request: Request):
    """
    Start Google OAuth registration with additional customer information.
    This endpoint stores the signup intent and redirects to Google OAuth.
    """
    client_id, _, redirect_uri, _ = _google_oauth_config()
    if not client_id:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")
    
    # Store signup intent in session/state (for production, use Redis/DB)
    state = secrets.token_urlsafe(24)
    signup_intent = {
        "org_name": signup_data.org_name,
        "org_slug": signup_data.org_slug,
        "account_type": signup_data.account_type,
        "api_key_name": signup_data.api_key_name,
    }
    
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    from fastapi.responses import RedirectResponse

    resp = RedirectResponse(url)
    # Store both state and signup intent in cookies (in production, use secure storage)
    resp.set_cookie("oauth_state", state, httponly=True, samesite="lax", max_age=300)
    resp.set_cookie("signup_intent", str(signup_intent), httponly=True, samesite="lax", max_age=300)
    return {"redirect_url": url}


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
        user=UserResponse.model_validate(user),
        organization=OrganizationResponse.model_validate(user.organization),
    )


# ========== EMAIL OTP LOGIN ENDPOINTS (SECURE) ==========

@router.post("/login/request-otp", response_model=OTPSentResponse)
async def request_login_otp_secure(
    request_data: LoginOTPRequest, 
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Request OTP for login (enhanced security version).
    - Validates user exists and is active
    - Implements rate limiting and IP blocking
    - Prevents email enumeration attacks
    - Logs all security events
    """
    otp_service = SecureOTPService(db)
    result = await otp_service.request_otp_secure(request_data.email, request)
    
    return OTPSentResponse(
        message=result["message"],
        email=result["email"]
    )


@router.post("/login/verify-otp", response_model=LoginResponse)
async def verify_login_otp_secure(
    request_data: OTPVerifyRequest, 
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Verify OTP and complete login (enhanced security version).
    - Implements brute force protection
    - Tracks failed attempts and blocks suspicious activity
    - Single-use OTP validation
    - Comprehensive security logging
    """
    # Verify user exists first
    user = db.query(User).filter(User.email == request_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Verify OTP using secure service
    otp_service = SecureOTPService(db)
    verification_success = await otp_service.verify_otp_secure(
        request_data.email, 
        request_data.otp_code, 
        request
    )
    
    if verification_success:
        # Generate JWT token (same as regular login)
        token_data = {
            "user_id": user.id,
            "org_id": user.org_id,
            "role": user.role,
        }
        access_token = create_jwt(token_data)
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserInfo(
                id=user.id,
                email=user.email
            )
        )


# ========== SECURITY MONITORING ENDPOINTS ==========

@router.get("/security/otp-stats")
async def get_otp_security_stats(
    hours: int = 24,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Get OTP security statistics (admin only).
    Shows request/verification rates, failures, and blocks.
    """
    otp_service = SecureOTPService(db)
    stats = otp_service.get_security_stats(hours=hours)
    return stats


@router.get("/security/otp-stats/user")
async def get_user_otp_stats(
    hours: int = 24,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get OTP security statistics for current user.
    """
    otp_service = SecureOTPService(db)
    stats = otp_service.get_security_stats(email=current_user.email, hours=hours)
    return stats


@router.post("/security/cleanup-expired")
async def cleanup_expired_security_data(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Clean up expired OTPs and old security logs (admin only).
    """
    otp_service = SecureOTPService(db)
    cleaned_count = otp_service.cleanup_expired_otps()
    return {
        "message": "Cleanup completed",
        "records_cleaned": cleaned_count
    }


# ========== API KEY MANAGEMENT ==========

@router.post("/api-keys", response_model=ApiKeyCreateResponse)
def create_api_key(
    key_data: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new API key for the current user.
    """
    # Generate API key
    api_key_plain = ApiKey.generate_key()
    api_key_hash = hash_password(api_key_plain)
    
    # Set expiry if specified
    expires_at = None
    if key_data.expires_in_days:
        from datetime import datetime, timedelta
        expires_at = datetime.utcnow() + timedelta(days=key_data.expires_in_days)
    
    api_key = ApiKey(
        user_id=current_user.id,
        key_name=key_data.key_name,
        key_hash=api_key_hash,
        key_prefix=api_key_plain[:8],
        scopes=key_data.scopes,
        expires_at=expires_at,
        is_active=True,
    )
    
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    return ApiKeyCreateResponse(
        api_key=api_key_plain,  # Only time the full key is shown
        key_info=ApiKeyResponse.model_validate(api_key)
    )


@router.get("/api-keys", response_model=List[ApiKeyResponse])
def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all API keys for the current user.
    """
    api_keys = db.query(ApiKey).filter(ApiKey.user_id == current_user.id).all()
    return [ApiKeyResponse.model_validate(key) for key in api_keys]


@router.delete("/api-keys/{key_id}")
def delete_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete/deactivate an API key.
    """
    api_key = db.query(ApiKey).filter(
        ApiKey.id == key_id,
        ApiKey.user_id == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    api_key.is_active = False
    db.commit()
    
    return {"message": "API key deactivated successfully"}


# ========== ENHANCED USER INFO ==========

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    """
    return UserResponse.model_validate(current_user)


@router.get("/org", response_model=OrganizationResponse)
def get_current_organization(current_user: User = Depends(get_current_user)):
    """
    Get current user's organization information.
    """
    return OrganizationResponse.model_validate(current_user.organization)


# --- RBAC: assign roles ---
VALID_ROLES = {"admin", "analyst", "operator"}


class AssignRoleBody(UserResponse.__class__):  # type: ignore[misc]
    pass


from pydantic import BaseModel


class AssignRoleRequest(BaseModel):
    user_id: int
    role: str


@router.post("/roles/assign", dependencies=[Depends(require_role("admin"))])
def assign_role(
    body: AssignRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Admin-only: assign a role to a user within the same organization.
    """
    role_norm = body.role.strip().lower()
    if role_norm not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Allowed: {sorted(VALID_ROLES)}")

    target = db.query(User).filter(User.id == body.user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.org_id != current_user.org_id:
        raise HTTPException(status_code=403, detail="Cannot assign role across organizations")

    target.role = role_norm
    db.commit()
    db.refresh(target)
    return {"ok": True, "user": UserResponse.from_orm(target)}


# --- Google OAuth minimal flow ---

def _google_oauth_config():
    client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
    frontend_base = os.getenv("BASE_URL", "http://localhost:3000")
    backend_base = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8010")
    redirect_uri = f"{backend_base}/v1/auth/oauth/google/callback"
    return client_id, client_secret, redirect_uri, frontend_base


@router.get("/oauth/google/start")
def google_oauth_start(request: Request):
    client_id, _, redirect_uri, _ = _google_oauth_config()
    if not client_id:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")
    # state for CSRF protection; store transiently in cookie
    state = secrets.token_urlsafe(24)
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    from fastapi.responses import RedirectResponse

    resp = RedirectResponse(url)
    resp.set_cookie("oauth_state", state, httponly=True, samesite="lax", max_age=300)
    return resp


@router.get("/oauth/google/callback")
async def google_oauth_callback(request: Request, db: Session = Depends(get_db)):
    """Enhanced Google OAuth callback that handles both login and registration"""
    client_id, client_secret, redirect_uri, frontend_base = _google_oauth_config()
    if not (client_id and client_secret):
        raise HTTPException(status_code=503, detail="Google OAuth not configured")

    params = dict(request.query_params)
    code = params.get("code")
    state = params.get("state")
    cookie_state = request.cookies.get("oauth_state")
    signup_intent_str = request.cookies.get("signup_intent")
    
    if not code or not state or (cookie_state and state != cookie_state):
        raise HTTPException(status_code=400, detail="Invalid OAuth state or code")

    # Exchange code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    
    email = None
    google_id = None
    name = None
    
    async with httpx.AsyncClient(timeout=10) as client:
        tok = await client.post(token_url, data=data)
        tok.raise_for_status()
        tjson = tok.json()
        id_token = tjson.get("id_token")
        
        # Parse ID token for user info
        from jose import jwt as jose_jwt
        try:
            claims = jose_jwt.get_unverified_claims(id_token)
            email = claims.get("email")
            google_id = claims.get("sub")
            name = claims.get("name")
        except Exception:
            pass

    if not email or not google_id:
        raise HTTPException(status_code=400, detail="Failed to retrieve user info from Google")

    # Check if user exists
    user = db.query(User).filter(User.email == email).first()
    
    if user:
        # Existing user login - add Google to auth providers if not already there
        if "google" not in user.auth_providers:
            auth_providers = user.auth_providers.copy()
            auth_providers.append("google")
            user.auth_providers = auth_providers
            user.google_id = google_id
            db.commit()
    else:
        # New user registration
        signup_intent = {}
        if signup_intent_str and signup_intent_str != "None":
            try:
                # Parse the stored signup intent (in production, use proper serialization)
                import ast
                signup_intent = ast.literal_eval(signup_intent_str)
            except:
                signup_intent = {}
        
        # Create organization if specified in signup intent
        org = None
        if signup_intent.get("org_name"):
            org_slug = signup_intent.get("org_slug") or slugify(signup_intent["org_name"])
            existing_org = db.query(Organization).filter(Organization.slug == org_slug).first()
            if existing_org:
                raise HTTPException(status_code=400, detail=f"Organization slug '{org_slug}' already exists")
            
            org = Organization(
                name=signup_intent["org_name"],
                slug=org_slug,
                is_active=True,
            )
            db.add(org)
            db.flush()
            role = "admin"  # First user in new org
        else:
            # Default organization for OAuth users
            org = db.query(Organization).filter(Organization.slug == "default").first()
            if not org:
                org = Organization(name="Default", slug="default", is_active=True)
                db.add(org)
                db.flush()
            role = "operator"
        
        # Create user
        user = User(
            email=email,
            hashed_password=None,  # No password for OAuth-only users
            full_name=name,
            role=role,
            org_id=org.id,
            is_active=True,
            account_type=signup_intent.get("account_type", "user"),
            auth_providers=["google"],
            google_id=google_id,
            is_email_verified=True,  # Google emails are pre-verified
        )
        db.add(user)
        db.flush()
        
        # Generate API key if requested for customers
        if signup_intent.get("api_key_name") and signup_intent.get("account_type") == "customer":
            api_key_plain = ApiKey.generate_key()
            api_key_hash = hash_password(api_key_plain)
            
            api_key = ApiKey(
                user_id=user.id,
                key_name=signup_intent["api_key_name"],
                key_hash=api_key_hash,
                key_prefix=api_key_plain[:8],
                scopes=["read"],
                is_active=True,
            )
            db.add(api_key)
        
        db.commit()
        db.refresh(user)

    # Issue JWT token
    token_data = {"user_id": user.id, "org_id": user.org_id, "role": user.role}
    access_token = create_jwt(token_data)

    # Redirect to frontend with token
    from fastapi.responses import RedirectResponse
    dest = f"{frontend_base}/dashboard?auth_token=" + urllib.parse.quote(access_token)
    response = RedirectResponse(dest)
    
    # Clear signup intent cookies
    response.delete_cookie("signup_intent")
    response.delete_cookie("oauth_state")
    
    return response
