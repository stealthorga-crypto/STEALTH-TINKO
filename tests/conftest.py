"""
Shared pytest fixtures for all test modules.
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import DB-related modules only (no app import at module import time)
from app.db import Base, get_db, SessionLocal, engine
from app.models import Organization, User, Transaction, RecoveryAttempt
from app.security import hash_password

# CI flags (evaluated once)
SKIP_DB = os.getenv("SKIP_DB") == "1"
SKIP_RAZORPAY_TESTS = os.getenv("SKIP_RAZORPAY_TESTS") == "1"

def pytest_collection_modifyitems(config, items):
    """Apply CI skip markers based on env flags without importing FastAPI app.

    - When SKIP_DB=1: skip all tests (hermetic CI, no DB/PSP)
    - Else, when SKIP_RAZORPAY_TESTS=1: skip tests whose nodeid mentions 'razorpay'
    """
    if SKIP_DB:
        skip_marker = pytest.mark.skip(reason="Skipping DB-dependent tests in CI (SKIP_DB=1)")
        for item in items:
            item.add_marker(skip_marker)
        return
    if SKIP_RAZORPAY_TESTS:
        rp_skip = pytest.mark.skip(reason="Skipping Razorpay tests in CI (SKIP_RAZORPAY_TESTS=1)")
        for item in items:
            nid = item.nodeid.lower()
            if "razorpay" in nid:
                item.add_marker(rp_skip)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all tables before running tests."""
    if SKIP_DB:
        # No-op in CI
        yield
        return
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def client():
    """
    Lazily create a TestClient. When SKIP_DB=1, return a dummy client that skips tests on use.
    """
    if SKIP_DB:
        class _Dummy:
            def __getattr__(self, _):
                def _skip(*a, **k):  # pragma: no cover
                    pytest.skip("SKIP_DB=1: client disabled in CI")
                return _skip
        return _Dummy()
    # Lazy import to avoid importing FastAPI app at module import time
    from app.main import app as _app
    with TestClient(_app) as c:
        yield c


@pytest.fixture(scope="function", autouse=True)
def clean_db():
    """Clean database before each test to ensure isolation."""
    if SKIP_DB:
        # No-op in CI
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
