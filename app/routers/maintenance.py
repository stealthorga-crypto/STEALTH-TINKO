from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.deps import get_db, require_roles
from app.models import User

router = APIRouter(prefix="/v1/maintenance", tags=["maintenance"])

@router.post("/partition/ensure_current", dependencies=[Depends(require_roles(["admin"]))])
def ensure_current_partition(current_user: User = Depends(), db: Session = Depends(get_db)):
    """Ensure current month partition exists (Postgres only). Safe to call multiple times."""
    try:
        db.execute(text("SELECT ensure_current_month_partitions();"))
        db.commit()
        return {"ok": True}
    except Exception:
        # No-op on unsupported databases or missing function
        db.rollback()
        return {"ok": True, "note": "ensure function not available; skipped"}
