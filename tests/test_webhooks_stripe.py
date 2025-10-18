import os
from unittest import mock

from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite:///./tinko_test.db")

from app.main import app  # noqa: E402
from app.db import Base, engine, SessionLocal  # noqa: E402
from app import models  # noqa: E402


client = TestClient(app)


def setup_module(module):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _mk_txn(ref: str, amount: int = 1000, currency: str = "inr"):
    db = SessionLocal()
    try:
        txn = models.Transaction(transaction_ref=ref, amount=amount, currency=currency)
        db.add(txn)
        db.commit()
        return txn
    finally:
        db.close()


def test_webhook_503_when_not_configured():
    os.environ.pop("STRIPE_WEBHOOK_SECRET", None)
    r = client.post("/v1/webhooks/stripe", data=b"{}", headers={"Stripe-Signature": "t=1"})
    assert r.status_code == 503


def test_webhook_records_event_with_mock():
    os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_x"
    _mk_txn("ref_wb_1")

    fake_event = {
        "type": "payment_intent.succeeded",
        "data": {
            "object": {
                "id": "pi_123",
                "description": "Recovery for ref_wb_1",
            }
        },
    }

    with mock.patch("app.routers.webhooks_stripe.stripe") as mstripe:
        mstripe.Webhook.construct_event.return_value = fake_event
        r = client.post(
            "/v1/webhooks/stripe",
            data=b"{}",
            headers={"Stripe-Signature": "t=1"},
        )
        assert r.status_code == 200
        assert r.json()["ok"] is True
