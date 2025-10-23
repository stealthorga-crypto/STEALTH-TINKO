from fastapi.testclient import TestClient

from app.main import app
from app.db import SessionLocal
from app.models import Organization, User, Transaction
from app.security import create_jwt


def seed_user_and_txn():
    db = SessionLocal()
    try:
        org = Organization(name="OrgR", slug="orgr")
        db.add(org); db.commit(); db.refresh(org)
        user = User(email="admin@r.test", hashed_password="x", role="admin", org_id=org.id, is_active=True)
        db.add(user); db.commit(); db.refresh(user)
        txn = Transaction(transaction_ref="R-T-1", amount=500, currency="INR", org_id=org.id)
        db.add(txn); db.commit();
        return user.id, org.id
    finally:
        db.close()


def test_recon_run_basic():
    uid, oid = seed_user_and_txn()
    client = TestClient(app)
    token = create_jwt({"user_id": uid, "org_id": oid, "role": "admin"})
    r = client.post("/v1/recon/run?days=1", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    j = r.json()
    assert set(j.keys()) >= {"checked", "ok", "mismatches"}
