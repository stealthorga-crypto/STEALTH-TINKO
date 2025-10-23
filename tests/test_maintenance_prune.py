from fastapi.testclient import TestClient

from app.main import app
from app.security import create_jwt


def test_prune_partitions_sqlite_noop():
    client = TestClient(app)
    token = create_jwt({"user_id": 1, "org_id": 1, "role": "admin"})
    r = client.post("/v1/maintenance/partitions/prune?months=6", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") is True
    assert isinstance(j.get("pruned"), list)