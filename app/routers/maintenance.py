from fastapi import APIRouter, Depends
from app.deps import require_roles
from app.services.partition_service import ensure_current_month_partitions

router = APIRouter(prefix="/v1/maintenance", tags=["maintenance"])

@router.post("/partition/ensure_current")
def ensure_current_partition(user=Depends(require_roles(["admin"]))):
    created = ensure_current_month_partitions()
    return {"ok": True, "created": created}
