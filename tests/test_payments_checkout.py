import os
from unittest import mock

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


def test_checkout_503_without_config():
    os.environ.pop("STRIPE_SECRET_KEY", None)
    _mk_txn("ref_chk_a")
    r = client.post(
        "/v1/payments/stripe/checkout",
        json={"transaction_ref": "ref_chk_a", "success_url": "https://example.com/s", "cancel_url": "https://example.com/c"},
    )
    assert r.status_code == 503


def test_checkout_success_with_mock():
    os.environ["STRIPE_SECRET_KEY"] = "sk_test_dummy"
    _mk_txn("ref_chk_b", 2199, "inr")
    with mock.patch("app.routers.payments.stripe") as mstripe:
        mstripe.checkout.Session.create.return_value = {"id": "cs_123", "url": "https://stripe.test/checkout/cs_123"}
        r = client.post(
            "/v1/payments/stripe/checkout",
            json={"transaction_ref": "ref_chk_b", "success_url": "https://example.com/s", "cancel_url": "https://example.com/c"},
        )
        assert r.status_code == 200
        j = r.json()
        assert j["ok"] is True
        assert j["data"]["url"].startswith("http")