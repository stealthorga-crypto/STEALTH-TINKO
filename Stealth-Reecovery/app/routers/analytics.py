"""
Analytics API endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.deps import get_current_user
from app.models import User
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
