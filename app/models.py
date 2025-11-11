from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, func, Boolean, UniqueConstraint
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
    email = Column(String(255), unique=True, nullable=True, index=True)  # Make nullable for mobile-only users
    hashed_password = Column(String(255), nullable=True)  # Make nullable for OAuth-only users
    full_name = Column(String(128), nullable=True)
    role = Column(String(32), nullable=False, default="operator")  # admin, analyst, operator
    is_active = Column(Boolean, default=True, nullable=False)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)  # Make nullable for customer users
    
    # Mobile authentication
    mobile_number = Column(String(20), unique=True, nullable=True, index=True)
    country_code = Column(String(5), nullable=True)  # e.g., "+91"
    mobile_verified = Column(Boolean, default=False, nullable=False)
    
    # OAuth and social authentication
    auth_providers = Column(JSON, nullable=False, default=["email"])  # ["email", "google", "mobile_otp", "microsoft"]
    google_id = Column(String(128), unique=True, nullable=True, index=True)  # Google user ID
    google_email = Column(String(255), nullable=True, index=True)  # Email from Google (might differ from primary)
    avatar_url = Column(String(500), nullable=True)  # Profile picture URL
    
    # Verification status
    is_email_verified = Column(Boolean, default=False, nullable=False)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    mobile_verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Account type and business info
    account_type = Column(String(32), nullable=False, default="user")  # user, customer, admin, guest
    auth_provider = Column(String(50), nullable=False, default="email")  # Primary auth method: email, google, mobile_otp
    
    # Login tracking
    last_login = Column(DateTime(timezone=True), nullable=True)
    login_count = Column(Integer, default=0, nullable=False)
    
    # Preferences
    preferred_language = Column(String(5), default="en", nullable=False)
    timezone = Column(String(50), default="UTC", nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    organization = relationship("Organization", back_populates="users")
    api_keys = relationship("ApiKey", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', mobile='{self.mobile_number}', auth_provider='{self.auth_provider}')>"


class ApiKey(Base):
    """API keys for customer integrations"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    key_name = Column(String(128), nullable=False)  # e.g., "Production API", "Staging API"
    key_hash = Column(String(255), nullable=False, unique=True, index=True)  # Hashed API key
    key_prefix = Column(String(16), nullable=False)  # First few chars for display (sk_...)
    
    # Permissions and scope
    scopes = Column(JSON, nullable=False, default=["read"])  # ["read", "write", "admin"]
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Usage tracking
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    usage_count = Column(Integer, default=0, nullable=False)
    
    # Expiry
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    user = relationship("User", back_populates="api_keys")
    
    @classmethod
    def generate_key(cls):
        """Generate a new API key with prefix"""
        import secrets
        key_id = secrets.token_urlsafe(32)
        return f"sk_{key_id}"
    
    def mask_key(self):
        """Return masked key for display"""
        return f"{self.key_prefix}...{self.key_hash[-4:]}"


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


class PspEvent(Base):
    """Idempotent store of PSP events to ensure single processing.

    psp_event_id should be a deterministic unique identifier, e.g.,
    provider + ':' + event_type + ':' + (payment_id or order_id).
    """
    __tablename__ = "psp_events"
    id = Column(Integer, primary_key=True)
    provider = Column(String(32), nullable=False)
    event_type = Column(String(64), nullable=False)
    psp_event_id = Column(String(160), nullable=False, unique=True, index=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class EmailOTP(Base):
    """Email OTP for authentication."""
    __tablename__ = "email_otps"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), index=True, nullable=False)
    otp_code = Column(String(6), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    
    @classmethod
    def generate_otp(cls):
        """Generate a 6-digit OTP code"""
        import random
        import string
        return ''.join(random.choices(string.digits, k=6))
    
    def is_expired(self):
        """Check if the OTP has expired"""
        from datetime import datetime
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """Check if OTP is valid (not used, not expired, attempts < 3)"""
        return not self.is_used and not self.is_expired() and self.attempts < 3
    
    def __repr__(self):
        return f"<EmailOTP(email='{self.email}', created_at='{self.created_at}', is_used={self.is_used})>"


class OTPSecurityLog(Base):
    """Track OTP security events and rate limiting"""
    __tablename__ = "otp_security_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), index=True, nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(String(500), nullable=True)
    action = Column(String(50), nullable=False)  # request_otp, verify_otp, failed_attempt, blocked
    success = Column(Boolean, nullable=False)
    attempt_count = Column(Integer, default=1, nullable=False)
    blocked_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<OTPSecurityLog(email='{self.email}', action='{self.action}', success={self.success})>"


class MobileOTP(Base):
    """Mobile OTP for SMS authentication."""
    __tablename__ = "mobile_otps"
    
    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String(20), index=True, nullable=False)
    otp_code = Column(String(6), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    @classmethod
    def generate_otp(cls):
        """Generate a 6-digit OTP code"""
        import random
        import string
        return ''.join(random.choices(string.digits, k=6))
    
    def is_expired(self):
        """Check if the OTP has expired"""
        from datetime import datetime
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """Check if OTP is valid (not used, not expired, attempts < 3)"""
        return not self.is_used and not self.is_expired() and self.attempts < 3
    
    def __repr__(self):
        return f"<MobileOTP(mobile='{self.mobile_number}', created_at='{self.created_at}', is_used={self.is_used})>"


class UserSession(Base):
    """Track user sessions for better security"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    device_info = Column(JSON, nullable=True)  # Browser, OS, device details
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    user = relationship("User")
    
    def __repr__(self):
        return f"<UserSession(user_id={self.user_id}, ip='{self.ip_address}', active={self.is_active})>"
