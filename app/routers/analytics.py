"""
Analytics API endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.deps import get_current_user, require_roles
from app.models import User, Transaction, FailureEvent, ReconLog
from datetime import datetime, timedelta, timezone
from app.services.stripe_service import StripeService
from app.services import analytics

router = APIRouter(prefix="/v1/analytics", tags=["Analytics"])

@router.get("/recovery_rate")
def get_recovery_rate(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recovery rate percentage over specified period."""
    return analytics.get_recovery_rate(db, current_user.org_id, days)

@router.get("/failure_categories")
def get_failure_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get breakdown of failure events by category."""
    return analytics.get_failure_categories(db, current_user.org_id)

@router.get("/revenue_recovered")
def get_revenue_recovered(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get total revenue recovered over period."""
    return analytics.get_revenue_recovered(db, current_user.org_id, days)

@router.get("/attempts_by_channel")
def get_attempts_by_channel(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recovery attempts breakdown by channel."""
    return analytics.get_attempts_by_channel(db, current_user.org_id)


@router.post("/recon/run", dependencies=[Depends(require_roles(["admin"]))])
def run_reconciliation(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run a read-only reconciliation against Stripe and record results.

    Returns counts: {checked, ok, mismatches}.
    """
    window_start = datetime.now(timezone.utc) - timedelta(days=days)

    # Find recent transactions for this org with Stripe IDs
    txns = db.query(Transaction).filter(
        Transaction.org_id == current_user.org_id,
        Transaction.created_at >= window_start,
        (Transaction.stripe_checkout_session_id.isnot(None)) | (Transaction.stripe_payment_intent_id.isnot(None))
    ).all()

    checked = 0
    ok = 0
    mismatches = 0

    for txn in txns:
        checked += 1
        # Determine internal status via event log heuristic
        paid_event = db.query(FailureEvent).filter(
            FailureEvent.transaction_id == txn.id,
            FailureEvent.reason == "payment_succeeded"
        ).first()
        internal_status = "paid" if paid_event else "unpaid"

        # Fetch external status
        external_status = None
        if txn.stripe_checkout_session_id:
            external_status = StripeService.get_session_status(txn.stripe_checkout_session_id)
        elif txn.stripe_payment_intent_id:
            pi_status = StripeService.get_payment_intent_status(txn.stripe_payment_intent_id)
            external_status = "paid" if pi_status == "succeeded" else "open"

        # Compare
        is_ok = (
            (internal_status == "paid" and external_status == "paid") or
            (internal_status == "unpaid" and external_status in ("open", None))
        )

        if is_ok:
            ok += 1
        else:
            mismatches += 1

        # Log recon result
        log = ReconLog(
            transaction_id=txn.id,
            stripe_checkout_session_id=txn.stripe_checkout_session_id,
            stripe_payment_intent_id=txn.stripe_payment_intent_id,
            internal_status=internal_status,
            external_status=external_status or "unknown",
            result="ok" if is_ok else "mismatch",
            details={"transaction_ref": txn.transaction_ref}
        )
        db.add(log)

    db.commit()

    return {"checked": checked, "ok": ok, "mismatches": mismatches}
