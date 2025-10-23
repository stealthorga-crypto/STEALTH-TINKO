import json
import hmac
import hashlib
import os
from fastapi.testclient import TestClient

from app.main import app
from app.db import SessionLocal
from app.models import Transaction, RecoveryAttempt, PspEvent


def _sign(body: bytes, secret: str) -> str:
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def test_razorpay_webhook_hmac_and_idempotent(monkeypatch):
    # Configure secret
    monkeypatch.setenv("RAZORPAY_WEBHOOK_SECRET", "shh")

    # Seed DB: transaction with order id and an attempt
    db = SessionLocal()
    try:
        txn = Transaction(transaction_ref="R-1", amount=1000, currency="INR", razorpay_order_id="order_123")
        db.add(txn); db.commit(); db.refresh(txn)
        att = RecoveryAttempt(transaction_id=txn.id, token="tok", status="sent", expires_at=txn.created_at)
        db.add(att); db.commit();
    finally:
        db.close()

    client = TestClient(app)
    payload = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_abc",
                    "order_id": "order_123",
                }
            }
        }
    }
    body = json.dumps(payload).encode()
    sig = _sign(body, "shh")

    r1 = client.post("/v1/payments/razorpay/webhooks", data=body, headers={"X-Razorpay-Signature": sig})
    assert r1.status_code == 200

    # Second call idempotent
    r2 = client.post("/v1/payments/razorpay/webhooks", data=body, headers={"X-Razorpay-Signature": sig})
    assert r2.status_code == 200
    assert r2.json().get("idempotent") in (True, None)

    # Ensure PspEvent recorded uniquely
    db = SessionLocal()
    try:
        count = db.query(PspEvent).count()
        assert count == 1
    finally:
        db.close()

def test_razorpay_webhook_invalid_signature(monkeypatch):
    monkeypatch.setenv("RAZORPAY_WEBHOOK_SECRET", "shh")
    client = TestClient(app)
    body = b"{}"
    # Wrong sig
    r = client.post("/v1/payments/razorpay/webhooks", data=body, headers={"X-Razorpay-Signature": "bad"})
    assert r.status_code == 400
