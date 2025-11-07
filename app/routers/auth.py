"""
Authentication router for user registration and login.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional
import re
import os
import secrets
import urllib.parse
import httpx

from ..deps import get_db, get_current_user, require_role
from ..models import User, Organization, EmailVerification
from ..security import hash_password, verify_password, create_jwt
from ..auth_schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    OrganizationResponse,
    TokenResponse,
    RegisterStartResponse,
    VerifyRequest,
    VerifyResponse,
)
from ..services.email_service import send_email
from ..services.auth0_otp_service import get_auth0_otp_service
from ..logging_config import get_logger
from datetime import datetime, timedelta, timezone

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
    
    # LEGACY path: immediate activation & JWT (kept for backward compatibility)
    # If you want OTP-first, use /v1/auth/register/start and /v1/auth/register/verify
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

    token_data = {"user_id": user.id, "org_id": user.org_id, "role": user.role}
    access_token = create_jwt(token_data)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user),
        organization=OrganizationResponse.from_orm(organization),
    )


def _generate_otp() -> str:
    import secrets
    # 6-digit numeric
    return f"{secrets.randbelow(1000000):06d}"


def _create_or_get_org(db: Session, name: str, slug_hint: str | None) -> Organization:
    org_slug = slug_hint or slugify(name)
    existing_org = db.query(Organization).filter(Organization.slug == org_slug).first()
    if existing_org:
        raise HTTPException(status_code=400, detail=f"Organization slug '{org_slug}' already exists")
    organization = Organization(name=name, slug=org_slug, is_active=True)
    db.add(organization)
    db.flush()
    return organization


@router.post("/register/start", response_model=RegisterStartResponse, status_code=status.HTTP_200_OK)
async def register_start(user_data: UserCreate, db: Session = Depends(get_db)):
    """Start registration by triggering Auth0 Passwordless Email OTP.

    Frontend flow: collect email, password, full_name, org_name; call this endpoint; then prompt for OTP.
    """
    logger = get_logger(__name__)
    otp_provider = os.getenv("OTP_PROVIDER", "smtp")
    
    # Validate input
    if not user_data.org_name:
        raise HTTPException(status_code=400, detail="Organization name required for new registration")
    
    # Check if email already registered
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user and existing_user.is_active:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Use Auth0 Passwordless OTP
    if otp_provider == "auth0":
        try:
            auth0_service = get_auth0_otp_service()
            success = await auth0_service.start(user_data.email)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send verification email. Please try again."
                )
            
            logger.info("auth0_otp_triggered", email=user_data.email)
            return RegisterStartResponse(ok=True, message="OTP sent to email")
            
        except Exception as e:
            logger.error("auth0_otp_error", email=user_data.email, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email. Please try again."
            )
    else:
        # Fallback to SMTP (legacy - should not be used in production)
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="SMTP OTP provider is deprecated. Use OTP_PROVIDER=auth0"
        )


@router.post("/register/verify", response_model=VerifyResponse)
async def register_verify(body: VerifyRequest, db: Session = Depends(get_db)):
    """Verify OTP with Auth0 and create/activate user in database."""
    logger = get_logger(__name__)
    otp_provider = os.getenv("OTP_PROVIDER", "smtp")
    
    if otp_provider == "auth0":
        try:
            # Verify OTP with Auth0
            auth0_service = get_auth0_otp_service()
            user_info = await auth0_service.verify(body.email, body.code)
            
            if not user_info or not user_info.get("email_verified"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired verification code"
                )
            
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == body.email).first()
            
            if existing_user and existing_user.is_active:
                # User already registered and verified
                logger.info("duplicate_registration_attempt", email=body.email)
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User already registered. Please sign in instead."
                )
            
            if existing_user:
                # User exists but not active, update and activate
                user = existing_user
                user.is_active = True
                user.hashed_password = hash_password(body.password)  # Update password
                user.full_name = body.full_name  # Update name
                logger.info("user_reactivated", email=body.email, user_id=user.id)
            else:
                # Create new organization
                organization = _create_or_get_org(db, body.org_name, body.org_slug)
                
                # Create new user
                hashed_pw = hash_password(body.password)
                user = User(
                    email=body.email,
                    hashed_password=hashed_pw,
                    full_name=body.full_name,
                    role="admin",
                    org_id=organization.id,
                    is_active=True,  # Verified by Auth0
                )
                db.add(user)
                logger.info("new_user_created", email=body.email)
            
            db.commit()
            db.refresh(user)
            logger.info("user_verified_and_created", email=body.email, user_id=user.id)
            
            return VerifyResponse(ok=True, message="Email verified. You can now sign in.")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("auth0_verify_error", email=body.email, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Verification failed. Please try again."
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="SMTP OTP provider is deprecated. Use OTP_PROVIDER=auth0"
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
            detail="User account is inactive or unverified",
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
    client_id, client_secret, redirect_uri, frontend_base = _google_oauth_config()
    if not (client_id and client_secret):
        raise HTTPException(status_code=503, detail="Google OAuth not configured")

    params = dict(request.query_params)
    code = params.get("code")
    state = params.get("state")
    cookie_state = request.cookies.get("oauth_state")
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
    async with httpx.AsyncClient(timeout=10) as client:
        tok = await client.post(token_url, data=data)
        tok.raise_for_status()
        tjson = tok.json()
        id_token = tjson.get("id_token")
        # Parse ID token (it's a JWT); we can do a light decode without verification for email claim
        from jose import jwt as jose_jwt
        try:
            claims = jose_jwt.get_unverified_claims(id_token)
            email = claims.get("email")
            name = claims.get("name")
        except Exception:
            email = None

    if not email:
        raise HTTPException(status_code=400, detail="Failed to retrieve email from Google")

    # Upsert organization and user minimally: put all SSO users into a default org if none exists
    org = db.query(Organization).filter(Organization.slug == "default").first()
    if not org:
        org = Organization(name="Default", slug="default", is_active=True)
        db.add(org)
        db.flush()

    user = db.query(User).filter(User.email == email).first()
    if not user:
        # SSO users default to operator role
        user = User(email=email, hashed_password=hash_password(secrets.token_urlsafe(12)), full_name=name if 'name' in locals() else None, role="operator", org_id=org.id, is_active=True)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Issue our JWT
    token_data = {"user_id": user.id, "org_id": user.org_id, "role": user.role}
    access_token = create_jwt(token_data)

    # Redirect to frontend with token
    from fastapi.responses import RedirectResponse
    dest = f"{frontend_base}/dashboard?auth_token=" + urllib.parse.quote(access_token)
    return RedirectResponse(dest)
