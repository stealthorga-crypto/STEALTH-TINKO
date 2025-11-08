from sqlalchemy import Column, String, DateTime, Boolean, Integer, func
from datetime import datetime, timedelta
import random
import string

# Import the same Base used by other models
from app.db import Base

class EmailOTP(Base):
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
        return ''.join(random.choices(string.digits, k=6))
    
    def is_expired(self):
        """Check if the OTP has expired"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """Check if OTP is valid (not used, not expired, attempts < 3)"""
        return not self.is_used and not self.is_expired() and self.attempts < 3
    
    def __repr__(self):
        return f"<EmailOTP(email='{self.email}', created_at='{self.created_at}', is_used={self.is_used})>"