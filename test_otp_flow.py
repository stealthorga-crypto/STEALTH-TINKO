"""
Complete OTP Registration & Login Test Script

Tests the entire user flow:
1. Start registration (trigger OTP)
2. Verify OTP code
3. Login with credentials
4. Access protected endpoint
"""

import requests
import json
import time

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

BASE_URL = "http://127.0.0.1:8010"

def print_step(step_num, message):
    print(f"\n{BLUE}━━━ STEP {step_num}: {message} ━━━{RESET}")

def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")

def print_error(message):
    print(f"{RED}✗ {message}{RESET}")

def print_info(message):
    print(f"{YELLOW}ℹ {message}{RESET}")

def print_json(data):
    print(json.dumps(data, indent=2))


def test_health_check():
    """Step 0: Check if backend is running"""
    print_step(0, "Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/healthz", timeout=5)
        if response.status_code == 200:
            print_success("Backend is running!")
            return True
        else:
            print_error(f"Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend")
        print_info(f"Make sure backend is running at {BASE_URL}")
        print_info("Run: uvicorn app.main:app --reload --host 127.0.0.1 --port 8010")
        return False
    except Exception as e:
        print_error(f"Health check failed: {str(e)}")
        return False


def test_registration_start():
    """Step 1: Start registration (trigger OTP email)"""
    print_step(1, "Start Registration (Trigger OTP Email)")
    
    test_email = f"test.user.{int(time.time())}@gmail.com"
    
    payload = {
        "email": test_email,
        "password": "SecurePassword123!",
        "full_name": "Test User",
        "org_name": "Test Organization"
    }
    
    print_info(f"Testing with email: {test_email}")
    print_info("Sending registration request...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/auth/register/start",
            json=payload,
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Registration started!")
            print_json(data)
            
            if data.get("ok"):
                print_success("✓ OTP email should be sent!")
                print_info("Check your email for the 6-digit code")
                return test_email, payload
            else:
                print_error("Registration start response was not OK")
                return None, None
        else:
            print_error(f"Registration failed with status {response.status_code}")
            print_json(response.json())
            return None, None
            
    except Exception as e:
        print_error(f"Registration start failed: {str(e)}")
        return None, None


def test_registration_verify(email, password, full_name, org_name):
    """Step 2: Verify OTP and complete registration"""
    print_step(2, "Verify OTP Code")
    
    print_info("Enter the 6-digit code from your email:")
    otp_code = input("OTP Code: ").strip()
    
    payload = {
        "email": email,
        "code": otp_code,
        "password": password,
        "full_name": full_name,
        "org_name": org_name
    }
    
    print_info("Verifying OTP...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/auth/register/verify",
            json=payload,
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("OTP verified!")
            print_json(data)
            
            if data.get("ok"):
                print_success("✓ User account created and activated!")
                return True
            else:
                print_error("Verification response was not OK")
                return False
        else:
            print_error(f"OTP verification failed with status {response.status_code}")
            print_json(response.json())
            return False
            
    except Exception as e:
        print_error(f"OTP verification failed: {str(e)}")
        return False


def test_login(email, password):
    """Step 3: Login with created account"""
    print_step(3, "Login with Credentials")
    
    payload = {
        "email": email,
        "password": password
    }
    
    print_info(f"Logging in as: {email}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/auth/login",
            json=payload,
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Login successful!")
            
            access_token = data.get("access_token")
            user = data.get("user")
            org = data.get("organization")
            
            print_info(f"User ID: {user.get('id')}")
            print_info(f"Email: {user.get('email')}")
            print_info(f"Name: {user.get('full_name')}")
            print_info(f"Role: {user.get('role')}")
            print_info(f"Organization: {org.get('name')}")
            print_info(f"Access Token: {access_token[:50]}...")
            
            return access_token
        else:
            print_error(f"Login failed with status {response.status_code}")
            print_json(response.json())
            return None
            
    except Exception as e:
        print_error(f"Login failed: {str(e)}")
        return None


def test_protected_endpoint(access_token):
    """Step 4: Access protected endpoint with token"""
    print_step(4, "Access Protected Endpoint")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    print_info("Accessing /v1/auth/me endpoint...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/v1/auth/me",
            headers=headers,
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Protected endpoint accessed successfully!")
            print_json(data)
            return True
        else:
            print_error(f"Protected endpoint failed with status {response.status_code}")
            print_json(response.json())
            return False
            
    except Exception as e:
        print_error(f"Protected endpoint access failed: {str(e)}")
        return False


def main():
    """Run complete OTP flow test"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  COMPLETE OTP REGISTRATION & LOGIN TEST{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    # Step 0: Health check
    if not test_health_check():
        print_error("\n❌ Backend is not running. Cannot proceed.")
        return
    
    # Step 1: Start registration
    email, payload = test_registration_start()
    if not email:
        print_error("\n❌ Registration start failed. Cannot proceed.")
        return
    
    # Step 2: Verify OTP
    if not test_registration_verify(
        email,
        payload["password"],
        payload["full_name"],
        payload["org_name"]
    ):
        print_error("\n❌ OTP verification failed. Cannot proceed.")
        return
    
    # Step 3: Login
    access_token = test_login(email, payload["password"])
    if not access_token:
        print_error("\n❌ Login failed. Cannot proceed.")
        return
    
    # Step 4: Access protected endpoint
    if not test_protected_endpoint(access_token):
        print_error("\n❌ Protected endpoint access failed.")
        return
    
    # Success!
    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}  ✓ ALL TESTS PASSED!{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")
    print(f"\n{YELLOW}Summary:{RESET}")
    print(f"  1. ✓ OTP email sent successfully")
    print(f"  2. ✓ OTP verified and user created")
    print(f"  3. ✓ Login successful")
    print(f"  4. ✓ Protected endpoint accessible")
    print(f"\n{GREEN}Your OTP flow is working perfectly!{RESET}\n")


if __name__ == "__main__":
    main()
