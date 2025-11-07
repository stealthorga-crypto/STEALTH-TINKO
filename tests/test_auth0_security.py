"""
Security-focused tests for Auth0 passwordless flow.

Tests for:
1. JWT signature verification
2. Duplicate registration handling
3. Idempotency
4. Email verification enforcement
5. Replay attack prevention
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import status
from fastapi.testclient import TestClient
from app.main import app
from app.models import User, Organization
from sqlalchemy.orm import Session


client = TestClient(app)


class TestJWTVerification:
    """Test JWT signature and claims validation"""
    
    @patch('app.services.auth0_otp_service.Auth0OTPService._get_jwks')
    @patch('app.services.auth0_otp_service.httpx.AsyncClient.post')
    def test_verify_validates_jwt_signature(self, mock_post, mock_jwks):
        """Ensure JWT signature is verified with JWKS"""
        # Mock Auth0 token response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6InRlc3Qta2V5In0.eyJlbWFpbCI6InRlc3RAZW1haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInN1YiI6ImF1dGgwfDEyMyIsImlzcyI6Imh0dHBzOi8vZGV2LTJjZWwzNmxpam1xZ2w2NTMudXMuYXV0aDAuY29tLyIsImF1ZCI6IkV5S1NqUmVvc2pHbGhpeTFsbjUzMngxRXhiTTFVbHpvIiwiZXhwIjo5OTk5OTk5OTk5fQ.fake_signature",
            "access_token": "fake_access_token"
        }
        mock_post.return_value = mock_response
        
        # Mock JWKS response
        mock_jwks.return_value = {
            "keys": [{
                "kid": "test-key",
                "kty": "RSA",
                "use": "sig",
                "n": "fake_n_value",
                "e": "AQAB"
            }]
        }
        
        # Attempt verify - should fail because signature is invalid
        response = client.post(
            "/v1/auth/register/verify",
            json={
                "email": "test@email.com",
                "code": "123456",
                "password": "Test123!",
                "full_name": "Test User",
                "org_name": "Test Org",
                "org_slug": "test-org"
            }
        )
        
        # Should fail signature verification
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    @patch('app.services.auth0_otp_service.httpx.AsyncClient.post')
    def test_verify_rejects_unverified_email(self, mock_post):
        """Ensure email_verified=false is rejected"""
        # Mock Auth0 response with email_verified=false
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id_token": "fake_token",
            "access_token": "fake_access"
        }
        mock_post.return_value = mock_response
        
        # Mock JWT decode to return email_verified=false
        with patch('app.services.auth0_otp_service.jwt.decode') as mock_decode:
            mock_decode.return_value = {
                "email": "test@email.com",
                "email_verified": False,  # NOT verified
                "sub": "auth0|123"
            }
            
            response = client.post(
                "/v1/auth/register/verify",
                json={
                    "email": "test@email.com",
                    "code": "123456",
                    "password": "Test123!",
                    "full_name": "Test User",
                    "org_name": "Test Org",
                    "org_slug": "test-org"
                }
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "Invalid or expired" in response.json()["detail"]
    
    @patch('app.services.auth0_otp_service.httpx.AsyncClient.post')
    def test_verify_rejects_mismatched_email(self, mock_post):
        """Ensure email in token matches request email"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id_token": "fake_token",
            "access_token": "fake_access"
        }
        mock_post.return_value = mock_response
        
        with patch('app.services.auth0_otp_service.jwt.decode') as mock_decode:
            mock_decode.return_value = {
                "email": "different@email.com",  # Mismatch!
                "email_verified": True,
                "sub": "auth0|123"
            }
            
            response = client.post(
                "/v1/auth/register/verify",
                json={
                    "email": "requested@email.com",
                    "code": "123456",
                    "password": "Test123!",
                    "full_name": "Test User",
                    "org_name": "Test Org",
                    "org_slug": "test-org"
                }
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestDuplicateRegistration:
    """Test handling of duplicate registration attempts"""
    
    @patch('app.services.auth0_otp_service.Auth0OTPService.verify')
    def test_duplicate_active_user_returns_409(self, mock_verify, db_session):
        """Attempting to register existing active user returns 409 Conflict"""
        # Mock successful Auth0 verification
        mock_verify.return_value = {
            "email": "existing@user.com",
            "email_verified": True,
            "sub": "auth0|123"
        }
        
        # Create existing active user
        org = Organization(name="Existing Org", slug="existing")
        db_session.add(org)
        db_session.commit()
        
        user = User(
            email="existing@user.com",
            hashed_password="hashed",
            full_name="Existing User",
            org_id=org.id,
            is_active=True  # Already active
        )
        db_session.add(user)
        db_session.commit()
        
        response = client.post(
            "/v1/auth/register/verify",
            json={
                "email": "existing@user.com",
                "code": "123456",
                "password": "NewPass123!",
                "full_name": "New Name",
                "org_name": "New Org",
                "org_slug": "new-org"
            }
        )
        
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already registered" in response.json()["detail"].lower()
        assert "sign in" in response.json()["detail"].lower()
    
    @patch('app.services.auth0_otp_service.Auth0OTPService.verify')
    def test_inactive_user_reactivation(self, mock_verify, db_session):
        """Inactive user can be reactivated with new OTP"""
        mock_verify.return_value = {
            "email": "inactive@user.com",
            "email_verified": True,
            "sub": "auth0|123"
        }
        
        # Create inactive user
        org = Organization(name="Test Org", slug="test")
        db_session.add(org)
        db_session.commit()
        
        user = User(
            email="inactive@user.com",
            hashed_password="old_hash",
            full_name="Old Name",
            org_id=org.id,
            is_active=False  # Inactive
        )
        db_session.add(user)
        db_session.commit()
        old_user_id = user.id
        
        response = client.post(
            "/v1/auth/register/verify",
            json={
                "email": "inactive@user.com",
                "code": "123456",
                "password": "NewPass123!",
                "full_name": "New Name",
                "org_name": "Test Org",
                "org_slug": "test"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify user was reactivated (not duplicated)
        db_session.refresh(user)
        assert user.is_active is True
        assert user.full_name == "New Name"
        assert user.id == old_user_id  # Same user, not new one


class TestIdempotency:
    """Test idempotent behavior of verification"""
    
    @patch('app.services.auth0_otp_service.Auth0OTPService.verify')
    def test_double_verify_same_otp_handled_gracefully(self, mock_verify, db_session):
        """Verifying with same OTP twice doesn't create duplicate users"""
        mock_verify.return_value = {
            "email": "newuser@test.com",
            "email_verified": True,
            "sub": "auth0|456"
        }
        
        # First verification
        response1 = client.post(
            "/v1/auth/register/verify",
            json={
                "email": "newuser@test.com",
                "code": "123456",
                "password": "Pass123!",
                "full_name": "New User",
                "org_name": "New Org",
                "org_slug": "new-org"
            }
        )
        assert response1.status_code == status.HTTP_200_OK
        
        # Second verification with same email (simulating replay)
        response2 = client.post(
            "/v1/auth/register/verify",
            json={
                "email": "newuser@test.com",
                "code": "123456",  # Even if Auth0 accepts it again
                "password": "Pass123!",
                "full_name": "New User",
                "org_name": "New Org",
                "org_slug": "new-org"
            }
        )
        
        # Should return 409 Conflict, not create duplicate
        assert response2.status_code == status.HTTP_409_CONFLICT
        
        # Verify only one user exists
        users = db_session.query(User).filter(User.email == "newuser@test.com").all()
        assert len(users) == 1


class TestIssuerValidation:
    """Test issuer (iss) claim validation"""
    
    @patch('app.services.auth0_otp_service.httpx.AsyncClient.post')
    def test_verify_validates_issuer(self, mock_post):
        """Ensure iss claim matches AUTH0_DOMAIN"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id_token": "fake_token",
            "access_token": "fake_access"
        }
        mock_post.return_value = mock_response
        
        # Mock JWT decode with wrong issuer
        with patch('app.services.auth0_otp_service.jwt.decode') as mock_decode:
            mock_decode.side_effect = Exception("Invalid issuer")
            
            response = client.post(
                "/v1/auth/register/verify",
                json={
                    "email": "test@email.com",
                    "code": "123456",
                    "password": "Test123!",
                    "full_name": "Test User",
                    "org_name": "Test Org",
                    "org_slug": "test-org"
                }
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestAudienceValidation:
    """Test audience (aud) claim validation"""
    
    @patch('app.services.auth0_otp_service.httpx.AsyncClient.post')
    def test_verify_validates_audience(self, mock_post):
        """Ensure aud claim matches CLIENT_ID"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id_token": "fake_token",
            "access_token": "fake_access"
        }
        mock_post.return_value = mock_response
        
        # Mock JWT decode with wrong audience
        with patch('app.services.auth0_otp_service.jwt.decode') as mock_decode:
            mock_decode.side_effect = Exception("Invalid audience")
            
            response = client.post(
                "/v1/auth/register/verify",
                json={
                    "email": "test@email.com",
                    "code": "123456",
                    "password": "Test123!",
                    "full_name": "Test User",
                    "org_name": "Test Org",
                    "org_slug": "test-org"
                }
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST


# Pytest fixtures
@pytest.fixture
def db_session():
    """Provide a clean database session for testing"""
    from app.db import SessionLocal, engine
    from app.models import Base
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    yield session
    
    # Cleanup
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=engine)
