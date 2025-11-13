"""
Direct test of Twilio Verify API to see exact error
"""
import os
from dotenv import load_dotenv
load_dotenv()

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
verify_service_sid = os.getenv("TWILIO_VERIFY_SERVICE_SID")

print("=" * 60)
print("Testing Twilio Verify API - Email OTP")
print("=" * 60)
print(f"Account SID: {account_sid}")
print(f"Service SID: {verify_service_sid}")
print()

test_email = input("Enter your Gmail address to test OTP: ").strip()

try:
    client = Client(account_sid, auth_token)
    
    print(f"\n📧 Sending OTP to: {test_email}")
    print("Please wait...")
    
    verification = client.verify \
        .v2 \
        .services(verify_service_sid) \
        .verifications \
        .create(to=test_email, channel='email')
    
    print("\n✅ SUCCESS!")
    print(f"Status: {verification.status}")
    print(f"SID: {verification.sid}")
    print(f"Channel: {verification.channel}")
    print(f"\nCheck your email: {test_email}")
    print("You should receive an OTP code from Twilio")
    
except TwilioRestException as e:
    print("\n❌ TWILIO API ERROR:")
    print(f"Error Code: {e.code}")
    print(f"Error Message: {e.msg}")
    print(f"Status: {e.status}")
    print(f"\nMore Info: {e.uri}")
    
except Exception as e:
    print("\n❌ UNEXPECTED ERROR:")
    print(f"Type: {type(e).__name__}")
    print(f"Message: {str(e)}")

print("\n" + "=" * 60)
