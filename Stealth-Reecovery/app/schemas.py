from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict

class CustomerIn(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None

class FailureEventIn(BaseModel):
    transaction_ref: str = Field(..., min_length=1, max_length=64)
    amount: Optional[int] = Field(None, ge=0, description="minor units (e.g., paise)")
    currency: Optional[str] = Field(None, min_length=3, max_length=8)
    gateway: Optional[str] = None
    failure_reason: str = Field(..., min_length=1)
    occurred_at: Optional[str] = None  # ISO 8601
    metadata: Optional[Dict[str, Any]] = None
    customer: Optional[CustomerIn] = None

class FailureEventOut(BaseModel):
    id: int
    transaction_id: int
    model_config = ConfigDict(from_attributes=True)
from typing import Optional
from pydantic import BaseModel, Field

class RecoveryLinkRequest(BaseModel):
    ttl_hours: float = Field(default=24, ge=0, le=168)
    channel: Optional[str] = "link"

class RecoveryLinkOut(BaseModel):
    attempt_id: int
    transaction_id: int
    token: str
    url: str
    expires_at: str
