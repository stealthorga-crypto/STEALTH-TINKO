"""
Razorpay payment endpoints (minimal): ping and order creation.
"""
from __future__ import annotations

import base64
import os
from typing import Optional
from datetime import datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models import Transaction, User
from app import models
from app.services.payments.razorpay_adapter import RazorpayAdapter
from app.analytics.sink import emit

router = APIRouter(prefix="/v1/payments/razorpay", tags=["Razorpay Payments"])


def _rp_auth_header() -> Optional[str]:
    key_id = os.getenv("RAZORPAY_KEY_ID")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET")
    if not key_id or not key_secret:
        return None
    token = base64.b64encode(f"{key_id}:{key_secret}".encode()).decode()
    return f"Basic {token}"


@router.get("/ping")
async def razorpay_ping():
    """Verify Razorpay credentials by listing 1 order (read-only)."""
    auth = _rp_auth_header()
    if not auth:
        raise HTTPException(status_code=503, detail="Razorpay not configured")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get("https://api.razorpay.com/v1/orders?count=1", headers={"Authorization": auth})
            if r.status_code == 200:
                return {"ok": True}
            raise HTTPException(status_code=502, detail="Razorpay ping failed")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail="Razorpay ping failed")


class CreateOrderIn(BaseModel):
    ref: str = Field(..., min_length=1, max_length=64)


class CreateOrderOut(BaseModel):
    order_id: str
    key_id: str
    amount: int
    currency: str


def _get_txn(db: Session, ref: str) -> Optional[Transaction]:
    return db.query(Transaction).filter(Transaction.transaction_ref == ref).first()


@router.post("/orders", response_model=CreateOrderOut)
async def create_order(body: CreateOrderIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    key_id = os.getenv("RAZORPAY_KEY_ID")
    if not key_id or not os.getenv("RAZORPAY_KEY_SECRET"):
        raise HTTPException(status_code=503, detail="Razorpay not configured")
    txn = _get_txn(db, body.ref)
    if not txn or not txn.amount or not txn.currency:
        raise HTTPException(status_code=404, detail="Transaction not found or incomplete")
    # Idempotency: if order already exists for this txn, return it
    if txn.razorpay_order_id:
        return CreateOrderOut(order_id=txn.razorpay_order_id, key_id=key_id, amount=int(txn.amount), currency=txn.currency.upper())
    # Create order via adapter
    try:
        adapter = RazorpayAdapter()
        res = adapter.create_order(amount=int(txn.amount), currency=txn.currency, receipt=txn.transaction_ref)
        order_id = res.get("order_id")
        if not order_id:
            raise HTTPException(status_code=502, detail="Invalid order response")
        txn.razorpay_order_id = order_id
        db.commit()
        return CreateOrderOut(order_id=order_id, key_id=key_id, amount=int(txn.amount), currency=txn.currency.upper())
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=502, detail="Failed to create order")


@router.post("/orders-public", response_model=CreateOrderOut)
async def create_order_public(body: CreateOrderIn, db: Session = Depends(get_db)):
    """Public endpoint to create a Razorpay order for a given transaction ref.
    Idempotent: returns existing order_id if already created.
    """
    key_id = os.getenv("RAZORPAY_KEY_ID")
    if not key_id or not os.getenv("RAZORPAY_KEY_SECRET"):
        raise HTTPException(status_code=503, detail="Razorpay not configured")
    txn = _get_txn(db, body.ref)
    if not txn or not txn.amount or not txn.currency:
        raise HTTPException(status_code=404, detail="Transaction not found or incomplete")
    if txn.razorpay_order_id:
        return CreateOrderOut(order_id=txn.razorpay_order_id, key_id=key_id, amount=int(txn.amount), currency=txn.currency.upper())
    try:
        adapter = RazorpayAdapter()
        res = adapter.create_order(amount=int(txn.amount), currency=txn.currency, receipt=txn.transaction_ref)
        order_id = res.get("order_id")
        if not order_id:
            raise HTTPException(status_code=502, detail="Invalid order response")
        txn.razorpay_order_id = order_id
        db.commit()
        return CreateOrderOut(order_id=order_id, key_id=key_id, amount=int(txn.amount), currency=txn.currency.upper())
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=502, detail="Failed to create order")


@router.post("/webhooks", include_in_schema=False)
async def razorpay_webhook(request, db: Session = Depends(get_db)):
    # FastAPI Request for body/headers
    from fastapi import Request as FastAPIRequest
    if not isinstance(request, FastAPIRequest):
        # When httpx.Request is passed by mistake, adapt to FastAPI request
        raise HTTPException(status_code=400, detail="Invalid request type")
    payload = await request.body()
    signature = request.headers.get("X-Razorpay-Signature")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")
    try:
        adapter = RazorpayAdapter()
        event = adapter.validate_webhook(payload, signature)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Process event types: payment.captured / order.paid
    etype = event.get("event") or event.get("event_type")
    payload_obj = event.get("payload") or {}
    order_id = None
    payment_id = None
    if "payment" in payload_obj:
        payment = payload_obj.get("payment", {}).get("entity", {})
        payment_id = payment.get("id")
        order_id = payment.get("order_id")
    elif "order" in payload_obj:
        order = payload_obj.get("order", {}).get("entity", {})
        order_id = order.get("id")

    if order_id:
        txn = db.query(Transaction).filter(Transaction.razorpay_order_id == order_id).first()
        if not txn:
            # Fallback: find by receipt (transaction_ref) if present
            receipt = payload_obj.get("order", {}).get("entity", {}).get("receipt") or payload_obj.get("payment", {}).get("entity", {}).get("notes", {}).get("receipt")
            if receipt:
                txn = db.query(Transaction).filter(Transaction.transaction_ref == receipt).first()
        if txn:
            # Idempotent update: if already completed with same payment_id, no-op
            if payment_id and txn.razorpay_payment_id == payment_id:
                return {"status": "ok", "idempotent": True}
            if etype in ("payment.captured", "order.paid"):
                txn.razorpay_payment_id = payment_id or txn.razorpay_payment_id
                # Mark a recovery attempt completed if exists
                attempt = db.query(models.RecoveryAttempt).filter(
                    (models.RecoveryAttempt.transaction_id == txn.id) | (models.RecoveryAttempt.transaction_ref == txn.transaction_ref)
                ).order_by(models.RecoveryAttempt.id.desc()).first()
                if attempt and attempt.status != "completed":
                    attempt.status = "completed"
                    attempt.used_at = datetime.utcnow()
                db.commit()
                try:
                    emit(
                        "payment_result",
                        {
                            "provider": "razorpay",
                            "order_id": order_id,
                            "payment_id": payment_id,
                            "transaction_ref": txn.transaction_ref,
                            "org_id": txn.org_id,
                            "status": "success",
                        },
                    )
                except Exception:
                    pass
    return {"status": "ok"}
