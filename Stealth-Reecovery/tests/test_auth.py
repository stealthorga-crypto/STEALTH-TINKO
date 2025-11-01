"""
Test suite for authentication endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import SessionLocal, Base, engine
from app.models import User, Organization

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Create all tables before running tests."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_db():
    """Clean database before each test."""
    db = SessionLocal()
    try:
        db.query(User).delete()
        db.query(Organization).delete()
        db.commit()
    finally:
        db.close()
    yield


def test_register_new_user():
    """Test user registration with new organization."""
    response = client.post(
        "/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User",
            "org_name": "Test Organization",
            "org_slug": "test-org"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["role"] == "admin"  # First user is admin
    assert data["organization"]["name"] == "Test Organization"
    assert data["organization"]["slug"] == "test-org"


def test_register_duplicate_email():
    """Test registration with already existing email."""
    # First registration
    client.post(
        "/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "org_name": "Test Org"
        }
    )
    
    # Duplicate registration
    response = client.post(
        "/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "AnotherPassword123!",
            "org_name": "Another Org"
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_register_duplicate_org_slug():
    """Test registration with already existing org slug."""
    # First registration
    client.post(
        "/v1/auth/register",
        json={
            "email": "user1@example.com",
            "password": "Password123!",
            "org_name": "Test Org",
            "org_slug": "test-org"
        }
    )
    
    # Duplicate org slug
    response = client.post(
        "/v1/auth/register",
        json={
            "email": "user2@example.com",
            "password": "Password123!",
            "org_name": "Test Org 2",
            "org_slug": "test-org"  # Same slug
        }
    )
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


def test_login_success():
    """Test successful login."""
    # Register first
    client.post(
        "/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "org_name": "Test Org"
        }
    )
    
    # Login
    response = client.post(
        "/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "SecurePassword123!"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"


def test_login_wrong_password():
    """Test login with incorrect password."""
    # Register first
    client.post(
        "/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "org_name": "Test Org"
        }
    )
    
    # Login with wrong password
    response = client.post(
        "/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "WrongPassword123!"
        }
    )
    
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_login_nonexistent_user():
    """Test login with non-existent email."""
    response = client.post(
        "/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        }
    )
    
    assert response.status_code == 401


def test_get_current_user():
    """Test getting current user info with valid token."""
    # Register and get token
    register_response = client.post(
        "/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "full_name": "Test User",
            "org_name": "Test Org"
        }
    )
    token = register_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert data["role"] == "admin"


def test_get_current_user_no_token():
    """Test getting current user without token."""
    response = client.get("/v1/auth/me")
    assert response.status_code == 403  # FastAPI HTTPBearer returns 403


def test_get_current_user_invalid_token():
    """Test getting current user with invalid token."""
    response = client.get(
        "/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    assert response.status_code == 401


def test_get_current_organization():
    """Test getting current user's organization."""
    # Register and get token
    register_response = client.post(
        "/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "org_name": "Test Organization",
            "org_slug": "test-org"
        }
    )
    token = register_response.json()["access_token"]
    
    # Get organization
    response = client.get(
        "/v1/auth/org",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Organization"
    assert data["slug"] == "test-org"
    assert data["is_active"] is True
