#!/bin/bash
# OTP Test Script - Run this to test the complete OTP flow

echo "==========================================="
echo "🧪 OTP TESTING SCRIPT"
echo "==========================================="
echo ""

# Generate unique email
EMAIL="testuser$(date +%s)@example.com"
echo "📧 Using email: $EMAIL"
echo ""

# Step 1: Register and send OTP
echo "Step 1: Registering user and sending OTP..."
echo "-------------------------------------------"
RESPONSE=$(curl -s -X POST http://127.0.0.1:8010/v1/auth/register/start \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"SecurePass123\",\"full_name\":\"Test User\",\"org_name\":\"Test Company\"}")

echo "Response: $RESPONSE"
echo ""

# Check if registration was successful
if echo "$RESPONSE" | grep -q '"ok":true'; then
    echo "✅ Registration successful!"
    echo ""
    echo "🔍 CHECK THE TERMINAL WHERE start-all.sh IS RUNNING"
    echo "    You should see a banner like:"
    echo "    ============================================================"
    echo "    🔐 OTP CODE FOR $EMAIL: XXXXXX"
    echo "    ============================================================"
    echo ""
    echo "📝 Enter the 6-digit OTP code from that banner:"
    read -p "OTP Code: " OTP_CODE
    
    # Step 2: Verify OTP
    echo ""
    echo "Step 2: Verifying OTP..."
    echo "-------------------------------------------"
    VERIFY_RESPONSE=$(curl -s -X POST http://127.0.0.1:8010/v1/auth/register/verify \
      -H "Content-Type: application/json" \
      -d "{\"email\":\"$EMAIL\",\"code\":\"$OTP_CODE\"}")
    
    echo "Response: $VERIFY_RESPONSE"
    echo ""
    
    # Check if verification was successful
    if echo "$VERIFY_RESPONSE" | grep -q '"ok":true'; then
        echo "✅ OTP VERIFICATION SUCCESSFUL!"
        echo "🎉 User is now verified and can sign in!"
        echo ""
        
        # Step 3: Test login
        echo "Step 3: Testing login..."
        echo "-------------------------------------------"
        LOGIN_RESPONSE=$(curl -s -X POST http://127.0.0.1:8010/v1/auth/login \
          -H "Content-Type: application/json" \
          -d "{\"email\":\"$EMAIL\",\"password\":\"SecurePass123\"}")
        
        echo "Response: $LOGIN_RESPONSE"
        echo ""
        
        if echo "$LOGIN_RESPONSE" | grep -q '"access_token"'; then
            echo "✅ LOGIN SUCCESSFUL!"
            echo "🔑 Access token received!"
            echo ""
            echo "==========================================="
            echo "✅ ALL TESTS PASSED!"
            echo "==========================================="
            echo ""
            echo "Summary:"
            echo "✅ User registration - SUCCESS"
            echo "✅ OTP generation - SUCCESS"
            echo "✅ OTP verification - SUCCESS"
            echo "✅ User authentication - SUCCESS"
        else
            echo "❌ Login failed"
        fi
    else
        echo "❌ OTP verification failed"
        echo "Possible reasons:"
        echo "  - Wrong OTP code entered"
        echo "  - OTP expired (10 minutes timeout)"
        echo "  - OTP already used"
    fi
else
    echo "❌ Registration failed"
    echo "Possible reasons:"
    if echo "$RESPONSE" | grep -q "already registered"; then
        echo "  - Email already exists (use a different email)"
    else
        echo "  - Backend not running"
        echo "  - Database connection issue"
        echo "  - Validation error"
    fi
fi

echo ""
echo "==========================================="
echo "Test completed"
echo "==========================================="
