from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _post(payload):
    r = client.post("/v1/classify", json=payload)
    assert r.status_code == 200
    j = r.json()
    assert j["ok"] is True
    return j["data"]


def test_known_code_issuer_declined():
    data = _post({"code": "issuer_declined", "message": None})
    assert data["category"] == "issuer_decline"
    assert "recommendation" in data


def test_message_auth_timeout():
    data = _post({"code": None, "message": "3DS authentication timeout"})
    assert data["category"] == "auth_timeout"


def test_message_funds():
    data = _post({"code": None, "message": "payment failed due to insufficient balance"})
    assert data["category"] == "funds"


def test_unknown_defaults():
    data = _post({"code": "weird_code", "message": "n/a"})
    assert data["category"] == "unknown"
    assert "alt" in data