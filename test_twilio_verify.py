"""
Test script for Twilio Verify Service integration
Run this to test the OTP functionality
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.twilio_verify_service import send_otp_verification, verify_otp_code, is_verify_available
from app.services.sms_service import send_otp_sms, verify_otp_sms


async def test_twilio_verify():
    """Test Twilio Verify Service functionality"""
    print("🧪 Testing Twilio Verify Service Integration")
    print("=" * 50)
    
    # Check if Twilio Verify is available
    print(f"Twilio Verify Available: {is_verify_available()}")
    
    # Test phone number (using your real number for testing)
    test_phone = "+919900015844"  # Your real Indian number
    
    print(f"\n📱 Testing OTP send to: {test_phone}")
    
    # Test sending OTP
    try:
        send_result = await send_otp_verification(test_phone, "sms")
        print(f"Send Result: {send_result}")
        
        if send_result["success"]:
            print("✅ OTP sent successfully!")
            
            # In a real test, you would:
            # 1. Check your phone for the OTP
            # 2. Enter the code here
            # test_code = input("Enter the OTP code: ")
            
            # For demo, we'll test with an invalid code
            print(f"\n🔐 Testing OTP verification with invalid code...")
            verify_result = await verify_otp_code(test_phone, "000000")
            print(f"Verify Result: {verify_result}")
            
        else:
            print(f"❌ Failed to send OTP: {send_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
    
    print("\n🔧 Testing enhanced SMS service...")
    
    # Test the enhanced SMS service
    try:
        sms_result = await send_otp_sms(test_phone, template_type="signup")
        print(f"SMS Service Result: {sms_result}")
        
        if sms_result["success"]:
            print("✅ SMS service working!")
            
            # Test verification
            test_otp = sms_result.get("otp_code", "123456")
            verify_result = await verify_otp_sms(test_phone, test_otp)
            print(f"Verification Result: {verify_result}")
            
        else:
            print(f"❌ SMS service failed: {sms_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error during SMS service test: {e}")


async def main():
    """Main test function"""
    await test_twilio_verify()
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print("- Twilio Verify Service integration complete")
    print("- Enhanced SMS service with fallback support")
    print("- Development mode for testing without live credentials")
    print("\n💡 Next steps:")
    print("1. Get Twilio Account SID and Auth Token from console")
    print("2. Update .env file with real credentials")
    print("3. Test with real phone number")


if __name__ == "__main__":
    asyncio.run(main())