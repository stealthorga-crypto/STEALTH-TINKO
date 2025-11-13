"""
Twilio Verify API OTP Service

Sends OTP codes via email using Twilio Verify API.
"""

import os
import random
import string
from typing import Optional, Dict
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from ..logging_config import get_logger

logger = get_logger(__name__)

# Test mode OTP storage (when TWILIO_VERIFY_SERVICE_SID is not set)
_test_otps: Dict[str, str] = {}


class TwilioOTPService:
    """Twilio Verify API OTP Service"""
    
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.verify_service_sid = os.getenv("TWILIO_VERIFY_SERVICE_SID")
        
        if not all([self.account_sid, self.auth_token]):
            raise ValueError(
                "Missing Twilio credentials. Required: "
                "TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN"
            )
        
        if not self.verify_service_sid:
            logger.warning("TWILIO_VERIFY_SERVICE_SID not set - running in TEST MODE")
            logger.warning("OTPs will be logged to console instead of sent via email")
            self.test_mode = True
        else:
            self.test_mode = False
            self.client = Client(self.account_sid, self.auth_token)
    
    def _generate_otp(self, length: int = 6) -> str:
        """Generate a random OTP code"""
        return ''.join(random.choices(string.digits, k=length))
    
    async def start(self, email: str) -> bool:
        """
        Generate and send OTP to user's email via Twilio Verify.
        
        Args:
            email: User's email address
            
        Returns:
            True if OTP was sent successfully, False otherwise
        """
        try:
            if self.test_mode:
                # Test mode - generate OTP and log to console
                otp = self._generate_otp()
                _test_otps[email] = otp
                logger.info("=" * 60)
                logger.info(f"TEST MODE - OTP for {email}: {otp}")
                logger.info("=" * 60)
                print(f"\n{'='*60}")
                print(f"🔐 TEST MODE - OTP CODE FOR {email}")
                print(f"    Code: {otp}")
                print(f"    Use this code to verify registration")
                print(f"{'='*60}\n")
                return True
            
            # Real Twilio Verify API call
            verification = self.client.verify \
                .v2 \
                .services(self.verify_service_sid) \
                .verifications \
                .create(to=email, channel='email')
            
            logger.info(
                "twilio_verify_otp_sent",
                email=email,
                status=verification.status,
                sid=verification.sid
            )
            return verification.status == 'pending'
            
        except TwilioRestException as e:
            logger.error(
                "twilio_verify_exception",
                email=email,
                error_code=e.code,
                error_message=e.msg
            )
            return False
        except Exception as e:
            logger.error(
                "twilio_verify_unexpected_exception",
                email=email,
                error=str(e)
            )
            return False
    
    async def verify(self, email: str, otp: str) -> Optional[Dict[str, any]]:
        """
        Verify OTP code.
        
        Args:
            email: User's email address
            otp: 6-digit OTP code from email
            
        Returns:
            Dict with user info if successful, None if verification failed
        """
        try:
            if self.test_mode:
                # Test mode - verify against stored OTP
                stored_otp = _test_otps.get(email)
                
                if not stored_otp:
                    logger.warning(f"TEST MODE - No OTP found for {email}")
                    return None
                
                if stored_otp != otp:
                    logger.warning(f"TEST MODE - OTP mismatch for {email}")
                    return None
                
                # Clear OTP after successful verification
                del _test_otps[email]
                logger.info(f"TEST MODE - OTP verified for {email}")
                
                return {
                    "email": email,
                    "email_verified": True
                }
            
            # Real Twilio Verify API call
            verification_check = self.client.verify \
                .v2 \
                .services(self.verify_service_sid) \
                .verification_checks \
                .create(to=email, code=otp)
            
            if verification_check.status == 'approved':
                logger.info(
                    "twilio_verify_otp_verified",
                    email=email,
                    status="success"
                )
                
                return {
                    "email": email,
                    "email_verified": True
                }
            else:
                logger.warning(
                    "twilio_verify_otp_failed",
                    email=email,
                    status=verification_check.status
                )
                return None
            
        except TwilioRestException as e:
            logger.error(
                "twilio_verify_check_exception",
                email=email,
                error_code=e.code,
                error_message=e.msg
            )
            return None
        except Exception as e:
            logger.error(
                "twilio_verify_unexpected_exception",
                email=email,
                error=str(e)
            )
            return None
