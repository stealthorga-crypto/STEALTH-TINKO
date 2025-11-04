import os
from unittest import mock

import pytest
from fastapi.testclient import TestClient

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


def test_create_intent_when_not_configured_returns_503():
    os.environ.pop("STRIPE_SECRET_KEY", None)
    _mk_txn("ref_no_stripe", 1234, "inr")
    r = client.post("/v1/payments/stripe/intents", json={"transaction_ref": "ref_no_stripe"})
    assert r.status_code == 503


def test_create_intent_success_with_mock():
    os.environ["STRIPE_SECRET_KEY"] = "sk_test_dummy"

    _mk_txn("ref_ok_1", 1299, "inr")

    with mock.patch("app.services.payments.stripe_adapter.stripe") as mstripe:
        mstripe.PaymentIntent.create.return_value = {
            "id": "pi_123",
            "client_secret": "cs_test_123",
            "amount": 1299,
            "currency": "inr",
            "status": "requires_payment_method",
        }
        r = client.post("/v1/payments/stripe/intents", json={"transaction_ref": "ref_ok_1"})
        assert r.status_code == 200
        j = r.json()
        assert j["ok"] is True
        assert j["data"]["client_secret"] == "cs_test_123"
