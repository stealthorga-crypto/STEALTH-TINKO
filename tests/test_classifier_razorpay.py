from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def classify(payload):
    r = client.post("/v1/classify", json=payload)
    assert r.status_code == 200
    return r.json()["data"]


def test_razorpay_insufficient_funds_soft():
    d = classify({"code": "RZP001_INSUFFICIENT_FUNDS"})
    assert d["hardness"] == "soft"
    assert d["category"] in ("funds",)


def test_razorpay_invalid_vpa_hard():
    d = classify({"code": "RZP_UPI_INVALID_VPA"})
    assert d["hardness"] == "hard"
    assert d["category"] in ("issuer_decline",)


def test_razorpay_unknown_falls_back():
    d = classify({"code": "RZP_SOMETHING_NEW"})
    assert d["category"] in ("unknown", "network", "funds", "auth_timeout", "issuer_decline", "upi_pending")