from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def post(payload):
    r = client.post("/v1/classify", json=payload)
    assert r.status_code == 200
    data = r.json()["data"]
    return data


def test_insufficient_funds_soft():
    d = post({"code": "insufficient_funds", "message": None})
    assert d["hardness"] == "soft"


def test_issuer_declined_hard():
    d = post({"code": "issuer_declined", "message": None})
    assert d["hardness"] == "hard"


def test_auth_timeout_soft():
    d = post({"code": "auth_timeout", "message": None})
    assert d["hardness"] == "soft"


def test_3ds_timeout_maps_soft():
    d = post({"code": "3ds_timeout", "message": None})
    assert d["hardness"] == "soft"


def test_unknown_defaults_soft():
    d = post({"code": "some_weird", "message": None})
    assert d["hardness"] == "soft"
