import os
from fastapi.testclient import TestClient

from app.main import app
from app.security import create_jwt


def test_trigger_due_requires_flag_and_admin(monkeypatch):
    client = TestClient(app)

    # Without flag -> 412
    token = create_jwt({"user_id": 1, "role": "admin", "org_id": 1})
    r = client.post("/v1/retry/trigger-due", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 412

    # Enable flag -> 200
    monkeypatch.setenv("FALLBACK_RETRY_RUNNER", "true")
    r2 = client.post("/v1/retry/trigger-due", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert r2.json().get("ok") is True
