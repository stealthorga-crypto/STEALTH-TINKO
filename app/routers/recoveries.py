from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..deps import get_db
from .. import models, schemas
import os

router = APIRouter(prefix="/v1/recoveries", tags=["recoveries"])

BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")

@router.post("/by_ref/{transaction_ref}/link", response_model=schemas.RecoveryLinkOut, status_code=status.HTTP_201_CREATED)
def create_link_by_ref(transaction_ref: str, body: schemas.RecoveryLinkRequest = schemas.RecoveryLinkRequest(), db: Session = Depends(get_db)):
    txn = db.query(models.Transaction).filter(models.Transaction.transaction_ref == transaction_ref).first()
    if txn is None:
        raise HTTPException(status_code=404, detail="transaction_ref not found")

    token = token_urlsafe(16)  # ~22-char URL-safe
    expires_at = datetime.now(timezone.utc) + timedelta(hours=body.ttl_hours)

    attempt = models.RecoveryAttempt(
        transaction_id=txn.id,
        # Default to email channel so notifications can be delivered via retry engine
        channel=body.channel or "email",
        token=token,
        status="created",
        expires_at=expires_at,
    )
    db.add(attempt); db.commit(); db.refresh(attempt)
    # Enqueue initial retry schedule based on active policy
    try:
        from app.tasks.retry_tasks import schedule_retry
        # Use org_id from transaction if available for policy lookup
        schedule_retry.delay(attempt.id, getattr(txn, 'org_id', None))
    except Exception:
        # Non-fatal if Celery not running; link creation should still succeed
        pass

    url = f"{BASE_URL}/pay/retry/{token}"
    return {
        "attempt_id": attempt.id,
        "transaction_id": txn.id,
        "token": token,
        "url": url,
        "expires_at": expires_at.isoformat(),
    }

@router.get("/by_ref/{transaction_ref}")
def list_attempts_by_ref(transaction_ref: str, db: Session = Depends(get_db)):
    txn = db.query(models.Transaction).filter(models.Transaction.transaction_ref == transaction_ref).first()
    if txn is None:
        return []
    rows = (
        db.query(models.RecoveryAttempt)
        .filter(models.RecoveryAttempt.transaction_id == txn.id)
        .order_by(models.RecoveryAttempt.id.desc())
        .all()
    )
    out = []
    for r in rows:
        out.append({
            "attempt_id": r.id,
            "transaction_id": r.transaction_id,
            "channel": r.channel,
            "token": r.token,
            "status": r.status,
            "expires_at": r.expires_at.isoformat() if r.expires_at else None,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "used_at": r.used_at.isoformat() if r.used_at else None,
            "url": f"{os.getenv('PUBLIC_BASE_URL','http://127.0.0.1:8000')}/pay/retry/{r.token}",
        })
    return out
