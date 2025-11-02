"""
Shared pytest fixtures for all test modules.
"""
import sys
import pathlib
import os

# Ensure repo root (parent of tests/) is on sys.path so `import app` works without PYTHONPATH
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db import Base, SessionLocal, engine
from app.models import Organization, User, Transaction, RecoveryAttempt
from app.security import hash_password


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all tables before running tests (skip drop in hermetic mode)."""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        # In hermetic CI (SKIP_DB=1), engine may be in-memory or a no-op
        pass
    yield
    try:
        if os.getenv("SKIP_DB", "").lower() not in ("1", "true", "yes"):
            Base.metadata.drop_all(bind=engine)
    except Exception:
        pass


@pytest.fixture(scope="function")
def client():
    """
    Create a test client for making HTTP requests.
    This fixture is required by test_stripe_integration.py.
    """
    return TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def clean_db():
    """Clean database before each test to ensure isolation (skip on SKIP_DB)."""
    if os.getenv("SKIP_DB", "").lower() in ("1", "true", "yes"):
        yield
        return
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
