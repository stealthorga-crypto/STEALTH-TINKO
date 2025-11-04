import os
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.main import app  # noqa: E402
from app.db import SessionLocal, Base, engine  # noqa: E402
from app import models  # noqa: E402


def setup_module(module):
    # Fresh schema each run
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_module(module):
    # Don't drop tables to keep dev DB; tests are idempotent
    pass


def _mk_attempt(token: str, status: str = "created", ttl_hours: float = 1.0, used: bool = False, opened: bool = False):
    db = SessionLocal()
    try:
        txn = models.Transaction(transaction_ref=f"ref_{token}")
        db.add(txn)
        db.flush()
        attempt = models.RecoveryAttempt(
            transaction_id=txn.id,
            transaction_ref=txn.transaction_ref,
            token=token,
            status=status,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=ttl_hours),
            opened_at=datetime.now(timezone.utc) if opened else None,
            used_at=datetime.now(timezone.utc) if used else None,
        )
        db.add(attempt)
        db.commit()
        return attempt
    finally:
        db.close()


client = TestClient(app)


def test_valid_token_flow():
    token = "tok_valid_1"
    _mk_attempt(token)

    r = client.get(f"/v1/recoveries/by_token/{token}")
    j = r.json()
    assert j["ok"] is True
    assert j["data"]["transaction_ref"].startswith("ref_")

    r2 = client.post(f"/v1/recoveries/by_token/{token}/open")
    j2 = r2.json()
    assert j2["ok"] is True
    assert j2["data"]["status"] in ("created", "opened")


def test_expired_token():
    token = "tok_expired_1"
    _mk_attempt(token, ttl_hours=-1)

    r = client.get(f"/v1/recoveries/by_token/{token}")
    j = r.json()
    assert j["ok"] is False
    assert j["error"]["code"] == "EXPIRED"


def test_used_token():
    token = "tok_used_1"
    _mk_attempt(token, used=True)

    r = client.get(f"/v1/recoveries/by_token/{token}")
    j = r.json()
    assert j["ok"] is False
    assert j["error"]["code"] == "USED"
