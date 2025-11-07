"""
Integration tests for Auth0 Passwordless Email OTP flow.

Tests the complete registration and login flow:
1. Send OTP via Auth0
2. Verify OTP and create user
3. Login with email + password
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.models import User, Organization
from sqlalchemy.orm import Session

client = TestClient(app)


class TestAuth0PasswordlessFlow:
    """Test Auth0 Passwordless OTP Registration + Login Flow"""
    
    @pytest.fixture
    def mock_auth0_start(self):
        """Mock Auth0 passwordless/start endpoint"""
        with patch("app.services.auth0_otp_service.Auth0OTPService.start") as mock:
            mock.return_value = AsyncMock(return_value=True)
            yield mock
    
    @pytest.fixture
    def mock_auth0_verify_success(self):
        """Mock successful Auth0 OTP verification"""
        with patch("app.services.auth0_otp_service.Auth0OTPService.verify") as mock:
            mock.return_value = AsyncMock(return_value={
                "email": "test@example.com",
                "email_verified": True,
                "sub": "auth0|123456",
                "name": "Test User"
            })
            yield mock
    
    @pytest.fixture
    def mock_auth0_verify_failure(self):
        """Mock failed Auth0 OTP verification"""
        with patch("app.services.auth0_otp_service.Auth0OTPService.verify") as mock:
            mock.return_value = AsyncMock(return_value=None)
            yield mock
    
    def test_register_start_calls_auth0(self, mock_auth0_start, db: Session):
        """Test that register/start triggers Auth0 passwordless/start"""
        response = client.post(
            "/v1/auth/register/start",
            json={
                "email": "test@example.com",
                "password": "SecurePass123!",
                "full_name": "Test User",
                "org_name": "Test Org"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert data["ok"] is True
        assert "message" in data
        
        # CRITICAL: Verify NO OTP in response
        response_text = response.text.lower()
        assert "otp" not in response_text or "otp sent" in response_text
        # Ensure no 6-digit code patterns
        import re
        assert not re.search(r'\b\d{6}\b', response_text)
        
        # Verify Auth0 service was called
        mock_auth0_start.assert_called_once()
    
    def test_register_start_returns_safe_message(self, mock_auth0_start):
        """Test that OTP send returns generic success without leaking OTP"""
        response = client.post(
            "/v1/auth/register/start",
            json={
                "email": "user@gmail.com",
                "password": "Test123!",
                "full_name": "User",
                "org_name": "Org"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Response should be generic
        assert data == {"ok": True, "message": "OTP sent to email"}
    
    def test_register_verify_creates_user_on_valid_otp(
        self, mock_auth0_verify_success, db: Session
    ):
        """Test that valid OTP creates user in database"""
        test_email = "newuser@example.com"
        
        response = client.post(
            "/v1/auth/register/verify",
            json={
                "email": test_email,
                "code": "123456",  # This should NEVER appear in logs
                "password": "SecurePass123!",
                "full_name": "New User",
                "org_name": "New Org"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["ok"] is True
        assert "verified" in data["message"].lower()
        
        # CRITICAL: Verify NO OTP in response
        assert "123456" not in response.text
        assert "code" not in response.json()
        
        # Verify user was created
        user = db.query(User).filter(User.email == test_email).first()
        assert user is not None
        assert user.is_active is True
        assert user.email == test_email
        
        # Verify Auth0 verify was called
        mock_auth0_verify_success.assert_called_once()
    
    def test_register_verify_fails_on_invalid_otp(
        self, mock_auth0_verify_failure, db: Session
    ):
        """Test that invalid OTP returns error without leaking details"""
        response = client.post(
            "/v1/auth/register/verify",
            json={
                "email": "test@example.com",
                "code": "999999",  # Invalid OTP
                "password": "SecurePass123!",
                "full_name": "Test",
                "org_name": "Test"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        
        # Should return generic error
        assert "invalid" in data["detail"].lower() or "expired" in data["detail"].lower()
        
        # CRITICAL: Should NOT leak OTP
        assert "999999" not in response.text
    
    def test_login_returns_jwt_for_valid_user(self, db: Session):
        """Test that login returns JWT token for verified user"""
        # First, create a verified user
        from app.security import hash_password
        from app.models import Organization
        
        org = Organization(name="Test Org", slug="test-org", is_active=True)
        db.add(org)
        db.flush()
        
        user = User(
            email="existing@example.com",
            hashed_password=hash_password("MyPassword123!"),
            full_name="Existing User",
            role="admin",
            org_id=org.id,
            is_active=True
        )
        db.add(user)
        db.commit()
        
        # Now try to login
        response = client.post(
            "/v1/auth/login",
            json={
                "email": "existing@example.com",
                "password": "MyPassword123!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify JWT structure
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == "existing@example.com"
        
        # Verify token is a valid JWT format
        token = data["access_token"]
        assert len(token.split(".")) == 3  # JWT has 3 parts
    
    def test_login_fails_for_invalid_credentials(self):
        """Test that login fails for wrong password"""
        response = client.post(
            "/v1/auth/login",
            json={
                "email": "user@example.com",
                "password": "WrongPassword!"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        
        # Should not leak whether user exists or password is wrong
        assert "incorrect" in data["detail"].lower()
    
    def test_no_otp_in_logs_during_flow(self, mock_auth0_start, mock_auth0_verify_success, caplog):
        """Test that OTP is NEVER logged during the entire flow"""
        import logging
        caplog.set_level(logging.DEBUG)
        
        # Send OTP
        client.post(
            "/v1/auth/register/start",
            json={
                "email": "test@example.com",
                "password": "Pass123!",
                "full_name": "Test",
                "org_name": "Org"
            }
        )
        
        # Verify OTP
        client.post(
            "/v1/auth/register/verify",
            json={
                "email": "test@example.com",
                "code": "654321",  # Test OTP
                "password": "Pass123!",
                "full_name": "Test",
                "org_name": "Org"
            }
        )
        
        # Check all log messages
        log_text = caplog.text.lower()
        
        # CRITICAL: OTP should NEVER appear in logs
        assert "654321" not in log_text
        assert "otp code" not in log_text
        assert "verification code is" not in log_text


class TestSecurityGuarantees:
    """Test security guarantees for OTP handling"""
    
    def test_otp_never_in_exception_messages(self):
        """Test that exceptions don't leak OTP codes"""
        # This would catch if any exception message contains the OTP
        response = client.post(
            "/v1/auth/register/verify",
            json={
                "email": "test@example.com",
                "code": "111111",
                "password": "Pass123!",
                "full_name": "Test",
                "org_name": "Org"
            }
        )
        
        # Even on error, response should not contain OTP
        assert "111111" not in response.text
    
    def test_response_headers_dont_leak_otp(self, mock_auth0_start):
        """Test that HTTP headers don't contain OTP"""
        response = client.post(
            "/v1/auth/register/start",
            json={
                "email": "test@example.com",
                "password": "Pass123!",
                "full_name": "Test",
                "org_name": "Org"
            }
        )
        
        # Check all headers
        headers_text = str(response.headers).lower()
        import re
        assert not re.search(r'\b\d{6}\b', headers_text)


# Pytest configuration for running tests
@pytest.fixture(scope="function")
def db():
    """Database fixture for tests"""
    from app.db import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
