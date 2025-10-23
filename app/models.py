from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, func, Boolean
from sqlalchemy.orm import relationship
from .db import Base

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    slug = Column(String(64), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    users = relationship("User", back_populates="organization")
    transactions = relationship("Transaction", back_populates="organization")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(128), nullable=True)
    role = Column(String(32), nullable=False, default="operator")  # admin, analyst, operator
    is_active = Column(Boolean, default=True, nullable=False)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    organization = relationship("Organization", back_populates="users")


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    transaction_ref = Column(String(64), unique=True, nullable=False, index=True)
    amount = Column(Integer, nullable=True)
    currency = Column(String(8), nullable=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # PSP-001: Stripe integration fields
    stripe_payment_intent_id = Column(String(128), nullable=True, index=True)
    stripe_checkout_session_id = Column(String(128), nullable=True, index=True)
    stripe_customer_id = Column(String(128), nullable=True, index=True)
    payment_link_url = Column(String(512), nullable=True)
    customer_email = Column(String(255), nullable=True)
    customer_phone = Column(String(32), nullable=True)

    # Razorpay integration fields
    razorpay_order_id = Column(String(128), nullable=True, index=True)
    razorpay_payment_id = Column(String(128), nullable=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    failure_events = relationship("FailureEvent", back_populates="transaction")
    organization = relationship("Organization", back_populates="transactions")

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

class RecoveryAttempt(Base):
    __tablename__ = "recovery_attempts"
    id = Column(Integer, primary_key=True)
    # Link to transaction either by id (FK) or by external ref for convenience
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=True, index=True)
    transaction_ref = Column(String(64), nullable=True, index=True)
    channel = Column(String(16), nullable=True)            # link/sms/email/whatsapp
    token = Column(String(64), unique=True, nullable=False, index=True)
    status = Column(String(24), nullable=False, default="created")  # created|sent|opened|completed|expired|cancelled
    expires_at = Column(DateTime(timezone=True), nullable=False)
    opened_at = Column(DateTime(timezone=True), nullable=True)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # RETRY-001: Retry tracking fields
    retry_count = Column(Integer, nullable=False, default=0)
    last_retry_at = Column(DateTime(timezone=True), nullable=True)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    max_retries = Column(Integer, nullable=False, default=3)  # Configurable per attempt
    
    # Relationships
    transaction = relationship("Transaction")
    notifications = relationship("NotificationLog", back_populates="recovery_attempt")


class NotificationLog(Base):
    """Log of all notification attempts (email, SMS, WhatsApp) for recovery attempts."""
    __tablename__ = "notification_logs"
    id = Column(Integer, primary_key=True)
    recovery_attempt_id = Column(Integer, ForeignKey("recovery_attempts.id", ondelete="CASCADE"), nullable=False, index=True)
    channel = Column(String(16), nullable=False)  # email, sms, whatsapp
    recipient = Column(String(255), nullable=False)  # email or phone number
    status = Column(String(24), nullable=False, default="pending")  # pending|sent|delivered|failed|bounced
    provider = Column(String(32), nullable=True)  # smtp, twilio, whatsapp_api, etc.
    provider_message_id = Column(String(128), nullable=True)  # External tracking ID
    error_message = Column(String(512), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    recovery_attempt = relationship("RecoveryAttempt", back_populates="notifications")


class RetryPolicy(Base):
    """Configurable retry policies per organization."""
    __tablename__ = "retry_policies"
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    max_retries = Column(Integer, nullable=False, default=3)
    initial_delay_minutes = Column(Integer, nullable=False, default=60)  # 1 hour
    backoff_multiplier = Column(Integer, nullable=False, default=2)  # Exponential: 1h, 2h, 4h
    max_delay_minutes = Column(Integer, nullable=False, default=1440)  # 24 hours cap
    enabled_channels = Column(JSON, nullable=False, default=["email"])  # ["email", "sms", "whatsapp"]
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    organization = relationship("Organization")


class ReconLog(Base):
    """Reconciliation results between internal state and PSP."""
    __tablename__ = "recon_logs"
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), index=True, nullable=False)
    stripe_checkout_session_id = Column(String(128), nullable=True)
    stripe_payment_intent_id = Column(String(128), nullable=True)
    internal_status = Column(String(32), nullable=False)
    external_status = Column(String(32), nullable=True)
    result = Column(String(16), nullable=False)  # ok | mismatch
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
