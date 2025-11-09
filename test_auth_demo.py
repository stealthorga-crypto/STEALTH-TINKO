"""
Test script demonstrating Ram's comprehensive authentication journey
Shows all supported registration and login methods.
"""
import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8010"  # Adjust to your backend URL
MAILHOG_URL = "http://localhost:8025"  # For checking emails

class AuthenticationDemo:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        
    def demo_ram_customer_journey(self):
        """Demonstrate Ram's complete authentication journey"""
        print("🚀 Starting Ram's Customer Authentication Journey")
        print("=" * 60)
        
        # Scenario 1: Traditional Email/Password Registration with API Keys
        print("\n📝 Scenario 1: Ram signs up with email/password + API keys")
        self.demo_email_password_signup()
        
        # Scenario 2: Google OAuth Registration  
        print("\n📝 Scenario 2: Ram signs up using Google OAuth")
        self.demo_google_oauth_signup()
        
        # Scenario 3: Login Methods for Existing User
        print("\n📝 Scenario 3: Ram's login options (existing user)")
        self.demo_existing_user_logins()
        
        print("\n🎉 Authentication Demo Complete!")
        
    def demo_email_password_signup(self):
        """Demo traditional signup with API key generation"""
        print("\n1️⃣ Email/Password Registration with API Keys")
        
        signup_data = {
            "email": "ram@example.com",
            "password": "SecurePassword123!",
            "full_name": "Ram Kumar",
            "org_name": "Ram's Business Solutions",
            "org_slug": "rams-business",
            "account_type": "customer",
            "api_key_name": "Production API Key"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/auth/register",
                json=signup_data
            )
            
            if response.status_code == 201:
                data = response.json()
                print("✅ Registration successful!")
                print(f"   User ID: {data['user']['id']}")
                print(f"   Organization: {data['organization']['name']}")
                print(f"   Account Type: {data['user']['account_type']}")
                print(f"   Auth Providers: {data['user']['auth_providers']}")
                
                # Check if API key was created
                token = data['access_token']
                self.check_api_keys(token)
                
            else:
                print(f"❌ Registration failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Registration error: {str(e)}")
    
    def demo_google_oauth_signup(self):
        """Demo Google OAuth registration flow"""
        print("\n2️⃣ Google OAuth Registration")
        
        # Step 1: Initiate Google OAuth with customer details
        signup_data = {
            "org_name": "Ram's Tech Startup",
            "org_slug": "rams-tech",
            "account_type": "customer",
            "api_key_name": "API Integration Key"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/auth/register/google",
                json=signup_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Google OAuth flow initiated!")
                print(f"   Redirect URL: {data['redirect_url']}")
                print("   📋 Steps for Ram:")
                print("      1. Visit the redirect URL")
                print("      2. Authorize with Google")
                print("      3. Complete registration with business details")
                print("      4. Receive API keys automatically")
                
            else:
                print(f"❌ OAuth initiation failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ OAuth error: {str(e)}")
    
    def demo_existing_user_logins(self):
        """Demo all login methods for existing users"""
        print("\n3️⃣ Login Options for Existing Users")
        
        # Method 1: Email/Password Login
        print("\n🔑 Method 1: Email/Password Login")
        self.demo_password_login()
        
        # Method 2: Email/OTP Login
        print("\n📧 Method 2: Email/OTP Login")
        self.demo_otp_login()
        
        # Method 3: Google OAuth Login
        print("\n🔍 Method 3: Google OAuth Login")
        print("   For existing Google-linked accounts:")
        print("   GET /v1/auth/oauth/google/start")
        print("   → Automatic login if account exists")
    
    def demo_password_login(self):
        """Demo traditional password login"""
        login_data = {
            "email": "ram@example.com",
            "password": "SecurePassword123!"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/auth/login",
                json=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Password login successful!")
                print(f"   Welcome back: {data['user']['full_name']}")
                print(f"   Token: {data['access_token'][:20]}...")
                
            else:
                print(f"❌ Password login failed: {response.status_code}")
                print(f"   Note: User may not exist yet")
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
    
    def demo_otp_login(self):
        """Demo OTP-based login"""
        print("\n   Step 1: Request OTP")
        
        try:
            # Request OTP
            response = self.session.post(
                f"{self.base_url}/v1/auth/login/request-otp",
                json={"email": "ram@example.com"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ OTP sent successfully!")
                print(f"   Message: {data['message']}")
                print(f"   Check emails at: {MAILHOG_URL}")
                
                # In a real scenario, Ram would check his email and enter OTP
                print("\n   Step 2: Verify OTP")
                print("   📋 Ram's next steps:")
                print("      1. Check email for 6-digit OTP")
                print("      2. POST /v1/auth/login/verify-otp")
                print("      3. Provide: {\"email\": \"ram@example.com\", \"otp_code\": \"123456\"}")
                
            else:
                print(f"❌ OTP request failed: {response.status_code}")
                print(f"   Note: User may not exist yet")
                
        except Exception as e:
            print(f"❌ OTP error: {str(e)}")
    
    def check_api_keys(self, token: str):
        """Check API keys for authenticated user"""
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = self.session.get(
                f"{self.base_url}/v1/auth/api-keys",
                headers=headers
            )
            
            if response.status_code == 200:
                api_keys = response.json()
                print(f"🔑 API Keys ({len(api_keys)} found):")
                for key in api_keys:
                    print(f"   - {key['key_name']}: {key['key_prefix']}...")
                    print(f"     Scopes: {key['scopes']}")
                    print(f"     Active: {key['is_active']}")
            else:
                print("   No API keys found")
                
        except Exception as e:
            print(f"❌ API key check error: {str(e)}")
    
    def demo_api_key_management(self, token: str):
        """Demo API key management for customers"""
        print("\n🔑 API Key Management Demo")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create new API key
        key_data = {
            "key_name": "Mobile App API",
            "scopes": ["read", "write"],
            "expires_in_days": 90
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/auth/api-keys",
                json=key_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ New API key created!")
                print(f"   Key: {data['api_key']}")
                print(f"   Name: {data['key_info']['key_name']}")
                print("   ⚠️ Save this key - it won't be shown again!")
                
        except Exception as e:
            print(f"❌ API key creation error: {str(e)}")

def main():
    """Run the authentication demo"""
    demo = AuthenticationDemo()
    
    print("🎯 Ram's Multi-Modal Authentication System Demo")
    print("This demonstrates all the ways Ram can sign up and sign in:")
    print("")
    print("📋 Supported Features:")
    print("   ✅ Email/Password registration & login")
    print("   ✅ Google OAuth registration & login")  
    print("   ✅ Email OTP login (for existing users)")
    print("   ✅ API key generation & management")
    print("   ✅ Customer account type support")
    print("   ✅ Organization management")
    print("")
    
    # Run the demo
    demo.demo_ram_customer_journey()
    
    print("\n📊 Summary of Authentication Flows:")
    print("   1. Ram signs up → Email/Password OR Google OAuth")
    print("   2. Ram provides business details → Organization created")
    print("   3. Ram requests API keys → Generated for customer accounts")
    print("   4. Ram signs in later → Email/Password OR Email/OTP OR Google")
    print("   5. All methods work with the SAME email address!")
    print("")
    print("🔒 Security Features:")
    print("   • OTP: 10min expiry, 3 attempts max, single-use")
    print("   • API Keys: Scoped permissions, usage tracking")
    print("   • JWT tokens: Secure session management")
    print("   • Multi-provider auth: Unified by email")

if __name__ == "__main__":
    main()