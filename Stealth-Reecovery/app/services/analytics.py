"""
Analytics service for recovery metrics and insights.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer, case
from datetime import datetime, timedelta
from app.models import RecoveryAttempt, Transaction, FailureEvent

def get_recovery_rate(db: Session, org_id: int, days: int = 30) -> dict:
    """Calculate recovery rate percentage based on failed vs recovered transactions."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    # Get total failed transactions in period
    total_failures = db.query(func.count(Transaction.id)).filter(
        Transaction.org_id == org_id,
        Transaction.created_at >= cutoff
    ).scalar() or 0
    
    # Get recovered transactions (those with completed recovery attempts)
    recovered = db.query(func.count(func.distinct(Transaction.id))).join(
        RecoveryAttempt
    ).filter(
        Transaction.org_id == org_id,
        Transaction.created_at >= cutoff,
        RecoveryAttempt.status == "completed"
    ).scalar() or 0
    
    rate = (recovered / total_failures) if total_failures > 0 else 0
    
    return {
        "recovery_rate": rate,
        "total_failures": total_failures,
        "recovered": recovered,
        "period_days": days
    }

def get_failure_categories(db: Session, org_id: int) -> dict:
    """Get failure event categories breakdown with percentages."""
    # Get total count for percentage calculation
    total_failures = db.query(func.count(FailureEvent.id)).join(Transaction).filter(
        Transaction.org_id == org_id
    ).scalar() or 1
    
    # Get breakdown by reason
    results = db.query(
        FailureEvent.reason,
        func.count(FailureEvent.id).label('count')
    ).join(Transaction).filter(
        Transaction.org_id == org_id
    ).group_by(FailureEvent.reason).all()
    
    categories = [
        {
            "category": r.reason,
            "count": r.count,
            "percentage": (r.count / total_failures * 100) if total_failures > 0 else 0
        }
        for r in results
    ]
    
    return {"categories": categories}

def get_revenue_recovered(db: Session, org_id: int, days: int = 30) -> dict:
    """Calculate total revenue recovered in period."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    total = db.query(func.sum(Transaction.amount)).join(
        RecoveryAttempt
    ).filter(
        Transaction.org_id == org_id,
        RecoveryAttempt.status == "completed",
        Transaction.created_at >= cutoff
    ).scalar() or 0
    
    return {
        "total_recovered": total,
        "currency": "usd",
        "period_days": days
    }

def get_attempts_by_channel(db: Session, org_id: int) -> dict:
    """Get recovery attempts breakdown by channel with success rates."""
    # Get all recovery attempts by channel
    results = db.query(
        RecoveryAttempt.channel,
        func.count(RecoveryAttempt.id).label('total'),
        func.sum(func.cast(RecoveryAttempt.status == "completed", Integer)).label('successful')
    ).join(Transaction).filter(
        Transaction.org_id == org_id
    ).group_by(RecoveryAttempt.channel).all()
    
    channels = [
        {
            "channel": r.channel or "payment_link",
            "count": r.total,
            "success_rate": (r.successful / r.total) if r.total > 0 else 0
        }
        for r in results
    ]
    
    return {"channels": channels}
