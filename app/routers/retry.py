import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..deps import get_db, require_roles_or_token
from ..tasks.retry_tasks import process_retry_queue

router = APIRouter(prefix="/v1/retry", tags=["retry"])


@router.post("/trigger-due")
def trigger_due_retries(
    _=Depends(require_roles_or_token(["admin"])),
    db: Session = Depends(get_db),
):
    """Trigger processing of due retries using in-process runner for local/dev.

    Controlled by env FALLBACK_RETRY_RUNNER=true; otherwise returns 412.
    """
    if os.getenv("FALLBACK_RETRY_RUNNER", "false").lower() not in ("1", "true", "yes"): 
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail="FALLBACK_RETRY_RUNNER disabled")

    # Call the Celery task function directly to run synchronously in-process
    result = process_retry_queue()
    return {"ok": True, **(result or {})}
