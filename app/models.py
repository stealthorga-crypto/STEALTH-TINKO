from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import relationship
from .db import Base

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    transaction_ref = Column(String(64), unique=True, nullable=False, index=True)
    amount = Column(Integer, nullable=True)
    currency = Column(String(8), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    failure_events = relationship("FailureEvent", back_populates="transaction")

class FailureEvent(Base):
    __tablename__ = "failure_events"
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    gateway = Column(String(32), nullable=True)
    reason = Column(String(128), nullable=False)
    # NOTE: attribute name must NOT be 'metadata'; keep SQL column name 'metadata' for compatibility
    meta = Column("metadata", JSON, nullable=True)
    occurred_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    transaction = relationship("Transaction", back_populates="failure_events")
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import relationship
from .db import Base

class RecoveryAttempt(Base):
    __tablename__ = "recovery_attempts"
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    channel = Column(String(16), nullable=True)            # link/sms/email/whatsapp
    token = Column(String(64), unique=True, nullable=False, index=True)
    status = Column(String(24), nullable=False, default="created")  # created|sent|opened|completed|expired|cancelled
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
