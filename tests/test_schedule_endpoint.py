from fastapi.testclient import TestClient

from app.main import app


def test_schedule_suggested_windows():
    client = TestClient(app)
    r = client.get("/v1/schedule/suggested_windows", params={"ref": "R-123", "hours_ahead": 6})
    assert r.status_code == 200
    j = r.json()
    assert j.get("ref") == "R-123"
    slots = j.get("slots")
    assert isinstance(slots, list) and len(slots) > 0
    first = slots[0]
    assert {"start", "end", "score"}.issubset(first.keys())
