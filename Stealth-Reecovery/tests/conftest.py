"""
Shared pytest fixtures for all test modules.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import Base, get_db, SessionLocal, engine
from app.models import Organization, User, Transaction, RecoveryAttempt
from app.security import hash_password


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all tables before running tests."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
    """
    Create a test client for making HTTP requests.
    This fixture is required by test_stripe_integration.py.
    """
    return TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def clean_db():
    """Clean database before each test to ensure isolation."""
    db = SessionLocal()
    try:
        # Clean in order to avoid FK constraints
        try:
            db.query(RecoveryAttempt).delete()
        except Exception:
            db.rollback()
        try:
            db.query(Transaction).delete()
        except Exception:
            db.rollback()
        db.query(User).delete()
        db.query(Organization).delete()
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()
    yield


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def test_org(db_session):
    """Create a test organization."""
    org = Organization(
        name="Test Org",
        slug="test-org",
        is_active=True
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture(scope="function")
def test_user(db_session, test_org):
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password=hash_password("testpass123"),
        full_name="Test User",
        role="admin",
        org_id=test_org.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = client.post(
        "/v1/auth/login",
        json={"email": test_user.email, "password": "testpass123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def test_transaction(db_session, test_org):
    """Create a test transaction."""
    transaction = Transaction(
        transaction_ref="TXN-STRIPE-001",
        amount=5000,  # $50.00
        currency="usd",
        org_id=test_org.id,
        customer_email="customer@example.com",
        customer_phone="+1234567890"
    )
    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)
    return transaction
