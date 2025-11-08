#!/usr/bin/env python3
"""
Simple test script for OTP functionality using MailHog
Run this to test the OTP system without full FastAPI setup
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import random
import string

# Set environment variables for testing
# Auto-detect if running inside Docker (use 'mailhog') or outside (use 'localhost')
default_smtp_host = 'localhost'  # Default to localhost for standalone testing
try:
    # Try to connect to mailhog first (Docker environment)
    import socket
    socket.create_connection(('mailhog', 1025), timeout=1)
    default_smtp_host = 'mailhog'
except:
    # Fall back to localhost (standalone environment)
    default_smtp_host = 'localhost'

os.environ.setdefault('SMTP_HOST', default_smtp_host)
os.environ.setdefault('SMTP_PORT', '1025')
os.environ.setdefault('SMTP_USE_TLS', 'false')
os.environ.setdefault('SMTP_FROM', 'noreply@stealth-recovery.dev')
os.environ.setdefault('SMTP_USER', '')
os.environ.setdefault('SMTP_PASSWORD', '')

class SimpleOTPService:
    """Simplified OTP service for testing"""
    
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'mailhog')
        self.smtp_port = int(os.getenv('SMTP_PORT', 1025))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.smtp_from = os.getenv('SMTP_FROM', 'noreply@stealth-recovery.dev')
        self.smtp_use_tls = os.getenv('SMTP_USE_TLS', 'false').lower() == 'true'
        print(f"SMTP Config: {self.smtp_host}:{self.smtp_port}, TLS: {self.smtp_use_tls}")
    
    @staticmethod
    def generate_otp():
        """Generate a 6-digit OTP code"""
        return ''.join(random.choices(string.digits, k=6))
    
    def send_otp_email(self, email: str, otp_code: str) -> bool:
        """Send OTP via email"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_from
            msg['To'] = email
            msg['Subject'] = "Your Login OTP - Tinko Recovery (TEST)"
            
            # Email body
            body = f"""
Hello,

Your login verification code is: {otp_code}

This is a TEST email from the OTP system.
This code will expire in 10 minutes.

Best regards,
Tinko Recovery Team
            """
            
            msg.attach(MIMEText(body.strip(), 'plain'))
            
            # Connect to SMTP server
            print(f"Connecting to SMTP server: {self.smtp_host}:{self.smtp_port}")
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            
            if self.smtp_use_tls:
                server.starttls()
                print("SMTP: Started TLS")
            
            # Login if credentials provided
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
                print("SMTP: Logged in with credentials")
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            print(f"✅ OTP email sent successfully to {email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending OTP email to {email}: {str(e)}")
            return False

def test_otp_system():
    """Test the OTP system"""
    print("=" * 60)
    print("TINKO RECOVERY - OTP SYSTEM TEST")
    print("=" * 60)
    
    # Initialize service
    otp_service = SimpleOTPService()
    
    # Generate OTP
    test_email = "test@example.com"
    otp_code = otp_service.generate_otp()
    
    print(f"\n📧 Test Email: {test_email}")
    print(f"🔑 Generated OTP: {otp_code}")
    print(f"⏰ Current Time: {datetime.now()}")
    
    # Send OTP
    print(f"\n📤 Sending OTP to {test_email}...")
    success = otp_service.send_otp_email(test_email, otp_code)
    
    if success:
        print(f"\n✅ SUCCESS! OTP sent successfully!")
        print(f"🌐 Check MailHog interface at: http://localhost:8025")
        print(f"🔍 Look for email with OTP: {otp_code}")
    else:
        print(f"\n❌ FAILED! Could not send OTP")
    
    print("\n" + "=" * 60)
    return success

if __name__ == "__main__":
    test_otp_system()