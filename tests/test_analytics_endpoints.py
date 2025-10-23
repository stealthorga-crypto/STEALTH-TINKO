from fastapi.testclient import TestClient

from app.main import app
from app.db import SessionLocal
from app.models import Organization, User
from app.security import create_jwt


def auth_headers(user_id: int, org_id: int, role: str = "operator"):
    token = create_jwt({"user_id": user_id, "org_id": org_id, "role": role})
    return {"Authorization": f"Bearer {token}"}


def seed_user():
    db = SessionLocal()
    try:
        org = Organization(name="OrgA", slug="orga")
        db.add(org); db.commit(); db.refresh(org)
        user = User(email="op@a.test", hashed_password="x", role="operator", org_id=org.id, is_active=True)
        db.add(user); db.commit(); db.refresh(user)
        return user.id, org.id
    finally:
        db.close()


def test_analytics_endpoints_shapes():
    uid, oid = seed_user()
    client = TestClient(app)
    h = auth_headers(uid, oid)

    r1 = client.get("/v1/analytics/revenue_recovered", headers=h)
    assert r1.status_code == 200
    j1 = r1.json()
    assert "currency" in j1 and "amount_cents" in j1

    r2 = client.get("/v1/analytics/recovery_rate", headers=h)
    assert r2.status_code == 200
    j2 = r2.json()
    assert "rate" in j2

    r3 = client.get("/v1/analytics/attempts_summary", headers=h)
    assert r3.status_code == 200
    j3 = r3.json()
    assert "by_status" in j3 and "by_channel" in j3
