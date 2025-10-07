from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..deps import get_db
from .. import models, schemas

router = APIRouter(prefix="/v1/events", tags=["events"])

@router.post("/payment_failed", response_model=schemas.FailureEventOut, status_code=status.HTTP_201_CREATED)
def payment_failed(payload: schemas.FailureEventIn, db: Session = Depends(get_db)):
    # Upsert transaction by external reference
    txn = db.query(models.Transaction).filter(models.Transaction.transaction_ref == payload.transaction_ref).first()
    if txn is None:
        txn = models.Transaction(
            transaction_ref=payload.transaction_ref,
            amount=payload.amount,
            currency=payload.currency,
        )
        db.add(txn); db.flush()
    else:
        if payload.amount is not None: txn.amount = payload.amount
        if payload.currency is not None: txn.currency = payload.currency

    # Parse occurred_at if provided (ISO 8601)
    occurred = None
    if payload.occurred_at:
        try:
            occurred = datetime.fromisoformat(payload.occurred_at.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid occurred_at. Use ISO-8601 (e.g., 2025-10-07T14:25:00Z).")

    # Build meta: prefer explicit payload.metadata; also keep any extra fields
    extras = payload.model_dump(exclude={"transaction_ref","amount","currency","gateway","failure_reason","occurred_at","metadata"})
    combined_meta = {}
    if payload.metadata: combined_meta["metadata"] = payload.metadata
    if extras: combined_meta["extras"] = extras

    fe = models.FailureEvent(
        transaction_id=txn.id,
        gateway=payload.gateway,
        reason=payload.failure_reason,
        meta=combined_meta or None,
        occurred_at=occurred,
    )
    db.add(fe); db.commit(); db.refresh(fe)
    return fe

@router.get("/by_ref/{transaction_ref}")
def list_events_by_ref(transaction_ref: str, db: Session = Depends(get_db)):
    txn = db.query(models.Transaction).filter(models.Transaction.transaction_ref == transaction_ref).first()
    if txn is None:
        return []
    rows = (
        db.query(models.FailureEvent)
        .filter(models.FailureEvent.transaction_id == txn.id)
        .order_by(models.FailureEvent.id.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "transaction_id": r.transaction_id,
            "gateway": r.gateway,
            "reason": r.reason,
            "occurred_at": r.occurred_at.isoformat() if r.occurred_at else None,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "meta": r.meta,
        } for r in rows
    ]
