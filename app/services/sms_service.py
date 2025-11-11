"""
SMS Service for sending OTP and notifications
Supports Twilio and Azure Communication Services
"""
import logging
from typing import Optional, Dict, Any
from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioException
from app.config import settings

logger = logging.getLogger(__name__)


class SMSService:
    """SMS service with multiple provider support"""
    
    def __init__(self):
        self.twilio_client = None
        self.provider = None
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize SMS provider based on available configuration"""
        # Try Twilio first
        if (settings.TWILIO_ACCOUNT_SID and 
            settings.TWILIO_AUTH_TOKEN and 
            settings.TWILIO_PHONE_NUMBER):
            try:
                self.twilio_client = TwilioClient(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
                self.provider = "twilio"
                logger.info("Twilio SMS provider initialized successfully")
                return
            except Exception as e:
                logger.error(f"Failed to initialize Twilio: {e}")
        
        # Could add Azure Communication Services here
        # if settings.AZURE_COMMUNICATION_CONNECTION_STRING:
        #     self.provider = "azure"
        
        logger.warning("No SMS provider configured. SMS functionality will be disabled.")
    
    async def send_otp(self, mobile_number: str, otp: str, template_type: str = "login") -> Dict[str, Any]:
        """
        Send OTP via SMS
        
        Args:
            mobile_number: Phone number in E.164 format (+1234567890)
            otp: 6-digit OTP code
            template_type: Type of OTP (login, signup, recovery)
            
        Returns:
            Dict with success status and details
        """
        if not self.provider:
            logger.error("No SMS provider available")
            return {
                "success": False,
                "error": "SMS service not configured",
                "provider": None
            }
        
        # Format mobile number to E.164 if needed
        formatted_number = self._format_mobile_number(mobile_number)
        if not formatted_number:
            return {
                "success": False,
                "error": "Invalid mobile number format",
                "provider": self.provider
            }
        
        # Create message based on template
        message = self._create_message(otp, template_type)
        
        # Send via configured provider
        if self.provider == "twilio":
            return await self._send_via_twilio(formatted_number, message)
        
        return {
            "success": False,
            "error": f"Unsupported provider: {self.provider}",
            "provider": self.provider
        }
    
    async def _send_via_twilio(self, mobile_number: str, message: str) -> Dict[str, Any]:
        """Send SMS via Twilio"""
        try:
            message_response = self.twilio_client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=mobile_number
            )
            
            logger.info(f"SMS sent successfully via Twilio: {message_response.sid}")
            
            return {
                "success": True,
                "provider": "twilio",
                "message_id": message_response.sid,
                "status": message_response.status,
                "to": mobile_number
            }
            
        except TwilioException as e:
            logger.error(f"Twilio SMS failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "twilio",
                "to": mobile_number
            }
        except Exception as e:
            logger.error(f"Unexpected SMS error: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "provider": "twilio",
                "to": mobile_number
            }
    
    def _format_mobile_number(self, mobile_number: str) -> Optional[str]:
        """
        Format mobile number to E.164 format
        
        Args:
            mobile_number: Raw mobile number
            
        Returns:
            Formatted number or None if invalid
        """
        # Remove all non-digit characters except +
        cleaned = ''.join(c for c in mobile_number if c.isdigit() or c == '+')
        
        # If no country code, assume US (+1) for now
        # In production, you'd want to detect country or ask user
        if not cleaned.startswith('+'):
            if len(cleaned) == 10:  # US number without country code
                cleaned = f"+1{cleaned}"
            elif len(cleaned) == 11 and cleaned.startswith('1'):  # US number with 1
                cleaned = f"+{cleaned}"
            elif len(cleaned) >= 10:  # International without +
                cleaned = f"+{cleaned}"
        
        # Basic validation - should be 10-15 digits after country code
        if len(cleaned) < 8 or len(cleaned) > 16:
            logger.warning(f"Invalid mobile number length: {cleaned}")
            return None
        
        return cleaned
    
    def _create_message(self, otp: str, template_type: str) -> str:
        """Create SMS message based on template type"""
        templates = {
            "login": f"Your TINKO login code: {otp}. Valid for 5 minutes. Don't share this code with anyone.",
            "signup": f"Welcome to TINKO! Your verification code: {otp}. Valid for 5 minutes.",
            "recovery": f"TINKO account recovery code: {otp}. Valid for 5 minutes. If you didn't request this, please ignore.",
            "payment": f"Your TINKO payment verification code: {otp}. Valid for 5 minutes."
        }
        
        return templates.get(template_type, templates["login"])
    
    async def send_recovery_notification(
        self, 
        mobile_number: str, 
        recovery_link: str, 
        amount: str, 
        merchant: str
    ) -> Dict[str, Any]:
        """
        Send payment recovery notification
        
        Args:
            mobile_number: Customer's mobile number
            recovery_link: Recovery link URL
            amount: Payment amount
            merchant: Merchant name
            
        Returns:
            Send result
        """
        if not self.provider:
            return {
                "success": False,
                "error": "SMS service not configured",
                "provider": None
            }
        
        formatted_number = self._format_mobile_number(mobile_number)
        if not formatted_number:
            return {
                "success": False,
                "error": "Invalid mobile number format",
                "provider": self.provider
            }
        
        message = (
            f"Payment Failed - TINKO Recovery\n"
            f"Merchant: {merchant}\n"
            f"Amount: {amount}\n"
            f"Complete payment: {recovery_link}\n"
            f"Link expires in 24 hours."
        )
        
        if self.provider == "twilio":
            return await self._send_via_twilio(formatted_number, message)
        
        return {
            "success": False,
            "error": f"Unsupported provider: {self.provider}",
            "provider": self.provider
        }
    
    def is_available(self) -> bool:
        """Check if SMS service is available"""
        return self.provider is not None
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about configured provider"""
        return {
            "provider": self.provider,
            "available": self.is_available(),
            "phone_number": settings.TWILIO_PHONE_NUMBER if self.provider == "twilio" else None
        }


# Global SMS service instance
sms_service = SMSService()


# Convenience functions
async def send_otp_sms(mobile_number: str, otp: str, template_type: str = "login") -> Dict[str, Any]:
    """Send OTP SMS"""
    return await sms_service.send_otp(mobile_number, otp, template_type)


async def send_recovery_sms(
    mobile_number: str, 
    recovery_link: str, 
    amount: str, 
    merchant: str
) -> Dict[str, Any]:
    """Send payment recovery SMS"""
    return await sms_service.send_recovery_notification(
        mobile_number, recovery_link, amount, merchant
    )


def is_sms_available() -> bool:
    """Check if SMS service is available"""
    return sms_service.is_available()