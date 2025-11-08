import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import EmailOTP
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

class OTPService:
    def __init__(self, db: Session):
        self.db = db
        self.smtp_host = os.getenv('SMTP_HOST', 'mailhog')
        self.smtp_port = int(os.getenv('SMTP_PORT', 1025))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.smtp_from = os.getenv('SMTP_FROM', 'noreply@stealth-recovery.dev')
        self.smtp_use_tls = os.getenv('SMTP_USE_TLS', 'false').lower() == 'true'
        
        logger.info(f"OTPService initialized with SMTP_HOST: {self.smtp_host}, SMTP_PORT: {self.smtp_port}")
    
    def generate_and_send_otp(self, email: str) -> bool:
        """Generate OTP and send via email"""
        try:
            # Invalidate any existing active OTPs for this email
            self.db.query(EmailOTP).filter(
                EmailOTP.email == email,
                EmailOTP.is_used == False
            ).update({"is_used": True})
            
            # Generate new OTP
            otp_code = EmailOTP.generate_otp()
            expires_at = datetime.utcnow() + timedelta(minutes=10)  # 10 minute expiry
            
            # Save OTP to database
            otp_record = EmailOTP(
                email=email,
                otp_code=otp_code,
                expires_at=expires_at
            )
            self.db.add(otp_record)
            self.db.commit()
            
            logger.info(f"Generated OTP for {email}: {otp_code}")
            
            # Send email
            self._send_otp_email(email, otp_code)
            return True
            
        except Exception as e:
            logger.error(f"Error generating OTP for {email}: {str(e)}")
            self.db.rollback()
            return False
    
    def verify_otp(self, email: str, otp_code: str) -> bool:
        """Verify the OTP code"""
        try:
            otp_record = self.db.query(EmailOTP).filter(
                EmailOTP.email == email,
                EmailOTP.otp_code == otp_code,
                EmailOTP.is_used == False
            ).first()
            
            if not otp_record:
                logger.warning(f"OTP verification failed: No valid OTP found for {email}")
                return False
            
            if not otp_record.is_valid():
                # Increment attempts if record exists
                otp_record.attempts += 1
                self.db.commit()
                logger.warning(f"OTP verification failed: Invalid OTP for {email} (expired/too many attempts)")
                return False
            
            # Mark OTP as used
            otp_record.is_used = True
            self.db.commit()
            
            logger.info(f"OTP verification successful for {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying OTP for {email}: {str(e)}")
            return False
    
    def _send_otp_email(self, email: str, otp_code: str):
        """Send OTP via email using configured SMTP"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_from
            msg['To'] = email
            msg['Subject'] = "Your Login OTP - Tinko Recovery"
            
            # Email body
            body = f"""
Hello,

Your login verification code is: {otp_code}

This code will expire in 10 minutes. Please use it to complete your login.

If you didn't request this code, please ignore this email.

Best regards,
Tinko Recovery Team
            """
            
            msg.attach(MIMEText(body.strip(), 'plain'))
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            
            if self.smtp_use_tls:
                server.starttls()
                logger.info("SMTP: Started TLS")
            
            # Login if credentials provided
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
                logger.info("SMTP: Logged in with credentials")
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            logger.info(f"OTP email sent successfully to {email}")
            
        except Exception as e:
            logger.error(f"Error sending OTP email to {email}: {str(e)}")
            raise
    
    def cleanup_expired_otps(self):
        """Clean up expired OTP records (optional maintenance)"""
        try:
            expired_count = self.db.query(EmailOTP).filter(
                EmailOTP.expires_at < datetime.utcnow()
            ).delete()
            
            self.db.commit()
            logger.info(f"Cleaned up {expired_count} expired OTP records")
            return expired_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired OTPs: {str(e)}")
            self.db.rollback()
            return 0