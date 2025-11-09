"""
Secure OTP Service with enhanced security features including:
- Rate limiting
- IP-based blocking
- User validation
- Anti-enumeration protection
- Brute force protection
- Comprehensive audit logging
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, Request
from typing import Optional
import logging
import os

from app.models import EmailOTP, OTPSecurityLog, User

# Set up logging
logger = logging.getLogger(__name__)

class SecureOTPService:
    def __init__(self, db: Session):
        self.db = db
        self.smtp_host = os.getenv('SMTP_HOST', 'mailhog')
        self.smtp_port = int(os.getenv('SMTP_PORT', 1025))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.smtp_from = os.getenv('SMTP_FROM', 'noreply@stealth-recovery.dev')
        self.smtp_use_tls = os.getenv('SMTP_USE_TLS', 'false').lower() == 'true'
        
        # Security settings
        self.max_requests_per_15min = 3
        self.max_failed_verifications_per_hour = 5
        self.temp_block_duration_minutes = 60
        self.otp_expiry_minutes = 10
        
        logger.info(f"SecureOTPService initialized with SMTP_HOST: {self.smtp_host}")
    
    async def request_otp_secure(self, email: str, request: Request) -> dict:
        """
        Secure OTP request with multiple validation layers
        """
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        # 1. Validate user exists and is active
        user = self.db.query(User).filter(
            User.email == email,
            User.is_active == True
        ).first()
        
        if not user:
            # Log failed attempt but don't reveal user doesn't exist
            self._log_security_event(
                email=email,
                ip_address=ip_address,
                user_agent=user_agent,
                action="request_otp",
                success=False
            )
            # Return success to prevent email enumeration
            return {
                "success": True,
                "message": "If this email exists, an OTP has been sent.",
                "email": email
            }
        
        # 2. Check if user/IP is currently blocked
        if self._is_blocked(email, ip_address):
            raise HTTPException(
                status_code=429,
                detail="Too many failed attempts. Please try again later."
            )
        
        # 3. Rate limiting - max requests per email per 15 minutes
        recent_requests = self.db.query(OTPSecurityLog).filter(
            OTPSecurityLog.email == email,
            OTPSecurityLog.action == "request_otp",
            OTPSecurityLog.created_at > datetime.utcnow() - timedelta(minutes=15)
        ).count()
        
        if recent_requests >= self.max_requests_per_15min:
            self._block_temporarily(email, ip_address, minutes=15)
            raise HTTPException(
                status_code=429,
                detail="Too many OTP requests. Please wait 15 minutes."
            )
        
        # 4. Check for active unused OTPs (prevent spam)
        active_otp = self.db.query(EmailOTP).filter(
            EmailOTP.email == email,
            EmailOTP.is_used == False,
            EmailOTP.expires_at > datetime.utcnow()
        ).first()
        
        if active_otp:
            # Don't generate new OTP if one is still valid
            self._log_security_event(
                email=email,
                ip_address=ip_address,
                user_agent=user_agent,
                action="request_otp",
                success=True
            )
            return {
                "success": True,
                "message": "OTP already sent. Check your email or wait for it to expire.",
                "email": email
            }
        
        # 5. Generate and send OTP
        try:
            # Invalidate any existing OTPs for this email
            self.db.query(EmailOTP).filter(
                EmailOTP.email == email,
                EmailOTP.is_used == False
            ).update({"is_used": True})
            
            otp_code = EmailOTP.generate_otp()
            expires_at = datetime.utcnow() + timedelta(minutes=self.otp_expiry_minutes)
            
            # Store OTP
            otp_record = EmailOTP(
                email=email,
                otp_code=otp_code,
                expires_at=expires_at
            )
            self.db.add(otp_record)
            self.db.commit()
            
            logger.info(f"Generated secure OTP for {email}: {otp_code}")
            
            # Send email
            self._send_otp_email(email, otp_code, user.full_name)
            
            # Log successful request
            self._log_security_event(
                email=email,
                ip_address=ip_address,
                user_agent=user_agent,
                action="request_otp",
                success=True
            )
            
            return {
                "success": True,
                "message": "OTP sent to your email",
                "email": email,
                "expires_in": self.otp_expiry_minutes * 60
            }
            
        except Exception as e:
            logger.error(f"Failed to send OTP to {email}: {str(e)}")
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Failed to send OTP. Please try again."
            )
    
    async def verify_otp_secure(self, email: str, otp_code: str, request: Request) -> bool:
        """
        Secure OTP verification with brute force protection
        Returns True if verification successful, raises HTTPException otherwise
        """
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        # Check if blocked
        if self._is_blocked(email, ip_address):
            raise HTTPException(
                status_code=429,
                detail="Too many failed attempts. Please try again later."
            )
        
        # Find valid OTP
        otp_record = self.db.query(EmailOTP).filter(
            EmailOTP.email == email,
            EmailOTP.otp_code == otp_code,
            EmailOTP.is_used == False
        ).first()
        
        if not otp_record or not otp_record.is_valid():
            # Increment attempts for all unused OTPs for this email
            self.db.query(EmailOTP).filter(
                EmailOTP.email == email,
                EmailOTP.is_used == False
            ).update({EmailOTP.attempts: EmailOTP.attempts + 1})
            
            self._log_security_event(
                email=email,
                ip_address=ip_address,
                user_agent=user_agent,
                action="verify_otp",
                success=False
            )
            
            # Check if too many failed attempts
            failed_attempts = self.db.query(OTPSecurityLog).filter(
                OTPSecurityLog.email == email,
                OTPSecurityLog.action == "verify_otp",
                OTPSecurityLog.success == False,
                OTPSecurityLog.created_at > datetime.utcnow() - timedelta(hours=1)
            ).count()
            
            if failed_attempts >= self.max_failed_verifications_per_hour:
                self._block_temporarily(email, ip_address, minutes=self.temp_block_duration_minutes)
                self.db.commit()
                raise HTTPException(
                    status_code=429,
                    detail="Too many failed verification attempts. Blocked for 1 hour."
                )
            
            self.db.commit()
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired OTP"
            )
        
        # Mark OTP as used
        otp_record.is_used = True
        self.db.commit()
        
        # Log successful verification
        self._log_security_event(
            email=email,
            ip_address=ip_address,
            user_agent=user_agent,
            action="verify_otp",
            success=True
        )
        
        logger.info(f"OTP verification successful for {email}")
        return True
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP considering proxies"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"
    
    def _is_blocked(self, email: str, ip_address: str) -> bool:
        """Check if user/IP combination is currently blocked"""
        block_record = self.db.query(OTPSecurityLog).filter(
            OTPSecurityLog.email == email,
            OTPSecurityLog.ip_address == ip_address,
            OTPSecurityLog.blocked_until.isnot(None),
            OTPSecurityLog.blocked_until > datetime.utcnow()
        ).first()
        
        is_blocked = block_record is not None
        if is_blocked:
            logger.warning(f"User {email} from IP {ip_address} is currently blocked until {block_record.blocked_until}")
        
        return is_blocked
    
    def _block_temporarily(self, email: str, ip_address: str, minutes: int):
        """Temporarily block user/IP combination"""
        block_until = datetime.utcnow() + timedelta(minutes=minutes)
        
        logger.warning(f"Temporarily blocking {email} from IP {ip_address} until {block_until}")
        
        # Create block record
        block_record = OTPSecurityLog(
            email=email,
            ip_address=ip_address,
            user_agent="system",
            action="blocked",
            success=False,
            blocked_until=block_until
        )
        self.db.add(block_record)
        # Don't commit here - let caller handle transaction
    
    def _log_security_event(self, email: str, ip_address: str, user_agent: str, 
                           action: str, success: bool):
        """Log security events for monitoring"""
        log_entry = OTPSecurityLog(
            email=email,
            ip_address=ip_address,
            user_agent=user_agent[:500] if user_agent else None,  # Truncate long user agents
            action=action,
            success=success
        )
        self.db.add(log_entry)
        # Don't commit here - let caller handle transaction
    
    def _send_otp_email(self, email: str, otp_code: str, user_name: Optional[str] = None):
        """Send OTP via email using configured SMTP with enhanced template"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_from
            msg['To'] = email
            msg['Subject'] = "Your Secure Login Code - Tinko Recovery"
            
            # Enhanced email template
            text_body = f"""
Hello {user_name or 'there'},

Your secure login verification code is: {otp_code}

This code will expire in {self.otp_expiry_minutes} minutes and can only be used once.

For your security:
- Do not share this code with anyone
- We will never ask for this code over the phone or email
- If you didn't request this code, please ignore this email

Best regards,
Tinko Recovery Security Team
            """.strip()
            
            html_body = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">🔐 Secure Login Code</h1>
                </div>
                
                <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; border: 1px solid #e9ecef;">
                    <p style="margin-top: 0;">Hello <strong>{user_name or 'there'}</strong>,</p>
                    
                    <p>Your secure login verification code is:</p>
                    
                    <div style="background: white; border: 2px dashed #667eea; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px;">
                        <div style="font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #667eea; font-family: 'Courier New', monospace;">
                            {otp_code}
                        </div>
                    </div>
                    
                    <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 6px; margin: 20px 0;">
                        <p style="margin: 0; color: #856404;"><strong>⏰ This code expires in {self.otp_expiry_minutes} minutes</strong></p>
                    </div>
                    
                    <div style="background: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 6px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #0c5460;">🛡️ Security Notice:</h3>
                        <ul style="margin-bottom: 0; color: #0c5460;">
                            <li>This code can only be used once</li>
                            <li>Never share this code with anyone</li>
                            <li>We will never ask for this code via phone or email</li>
                            <li>If you didn't request this, please ignore this email</li>
                        </ul>
                    </div>
                    
                    <p style="color: #6c757d; font-size: 14px; margin-bottom: 0;">
                        Best regards,<br>
                        <strong>Tinko Recovery Security Team</strong>
                    </p>
                </div>
            </div>
            """
            
            # Attach both plain text and HTML versions
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
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
            
            logger.info(f"Secure OTP email sent successfully to {email}")
            
        except Exception as e:
            logger.error(f"Error sending secure OTP email to {email}: {str(e)}")
            raise
    
    def cleanup_expired_otps(self) -> int:
        """Clean up expired OTP records and security logs (maintenance)"""
        try:
            # Clean up expired OTPs
            expired_otps = self.db.query(EmailOTP).filter(
                EmailOTP.expires_at < datetime.utcnow()
            ).delete()
            
            # Clean up old security logs (keep 30 days)
            old_logs = self.db.query(OTPSecurityLog).filter(
                OTPSecurityLog.created_at < datetime.utcnow() - timedelta(days=30)
            ).delete()
            
            self.db.commit()
            logger.info(f"Cleaned up {expired_otps} expired OTPs and {old_logs} old security logs")
            return expired_otps + old_logs
            
        except Exception as e:
            logger.error(f"Error cleaning up expired records: {str(e)}")
            self.db.rollback()
            return 0
    
    def get_security_stats(self, email: str = None, hours: int = 24) -> dict:
        """Get security statistics for monitoring"""
        try:
            base_query = self.db.query(OTPSecurityLog).filter(
                OTPSecurityLog.created_at > datetime.utcnow() - timedelta(hours=hours)
            )
            
            if email:
                base_query = base_query.filter(OTPSecurityLog.email == email)
            
            total_requests = base_query.filter(OTPSecurityLog.action == "request_otp").count()
            successful_requests = base_query.filter(
                OTPSecurityLog.action == "request_otp",
                OTPSecurityLog.success == True
            ).count()
            
            total_verifications = base_query.filter(OTPSecurityLog.action == "verify_otp").count()
            successful_verifications = base_query.filter(
                OTPSecurityLog.action == "verify_otp",
                OTPSecurityLog.success == True
            ).count()
            
            blocked_attempts = base_query.filter(OTPSecurityLog.action == "blocked").count()
            
            return {
                "period_hours": hours,
                "email": email,
                "otp_requests": {
                    "total": total_requests,
                    "successful": successful_requests,
                    "failed": total_requests - successful_requests
                },
                "otp_verifications": {
                    "total": total_verifications,
                    "successful": successful_verifications,
                    "failed": total_verifications - successful_verifications
                },
                "security_blocks": blocked_attempts,
                "success_rate": {
                    "requests": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
                    "verifications": (successful_verifications / total_verifications * 100) if total_verifications > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting security stats: {str(e)}")
            return {"error": str(e)}