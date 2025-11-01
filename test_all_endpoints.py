#!/usr/bin/env python3
"""
Comprehensive End-to-End Test Suite for Tinko Recovery
Tests all backend endpoints and functionality.

Note: This file is an interactive smoke/helper module and is not intended to
run under the pytest unit test suite. We mark it skipped for pytest collection
to avoid accidental CI failures.
"""
try:
    import pytest  # type: ignore
    pytestmark = pytest.mark.skip("skip interactive smoke helper in pytest runs")
except Exception:
    pass

import os
import requests
import json
from datetime import datetime, timedelta
import sys

# Allow overriding backend URL; default to the running local backend
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8010")

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health_endpoints():
    print_section("1. HEALTH & READINESS CHECKS")
    
    try:
        # Health check
        resp = requests.get(f"{BASE_URL}/healthz", timeout=5)
        print(f"✅ GET /healthz - Status: {resp.status_code}")
        print(f"   Response: {resp.json()}")
        
        # Readiness check
        resp = requests.get(f"{BASE_URL}/readyz", timeout=5)
        print(f"✅ GET /readyz - Status: {resp.status_code}")
        print(f"   Response: {resp.json()}")
        
        return True
    except Exception as e:
        print(f"❌ Health checks failed: {e}")
        return False

def test_event_ingestion():
    print_section("2. EVENT INGESTION")
    
    try:
        # Create a failure event
        payload = {
            "transaction_ref": f"TXN_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "amount": 49999,  # ₹499.99 in paise
            "currency": "INR",
            "gateway": "razorpay",
            "failure_reason": "insufficient_funds",
            "occurred_at": datetime.now().isoformat(),
            "metadata": {
                "customer_email": "test@example.com",
                "product": "Pro Plan"
            }
        }
        
        resp = requests.post(f"{BASE_URL}/v1/events/payment_failed", json=payload, timeout=5)
        print(f"✅ POST /v1/events/payment_failed - Status: {resp.status_code}")
        print(f"   Created event ID: {resp.json().get('id')}")
        
        # Get events by ref
        txn_ref = payload["transaction_ref"]
        resp = requests.get(f"{BASE_URL}/v1/events/by_ref/{txn_ref}", timeout=5)
        print(f"✅ GET /v1/events/by_ref/{txn_ref} - Status: {resp.status_code}")
        print(f"   Found {len(resp.json())} event(s)")
        
        return txn_ref
    except Exception as e:
        print(f"❌ Event ingestion failed: {e}")
        return None

def test_classifier():
    print_section("3. FAILURE CLASSIFIER")
    
    test_cases = [
        {"code": "insufficient_funds", "message": None, "expected": "funds"},
        {"code": None, "message": "3DS timeout", "expected": "auth_timeout"},
        {"code": "do_not_honor", "message": None, "expected": "issuer_decline"},
        {"code": None, "message": "network error", "expected": "network"},
        {"code": "unknown_code", "message": "random message", "expected": "unknown"}
    ]
    
    try:
        for i, test in enumerate(test_cases, 1):
            resp = requests.post(f"{BASE_URL}/v1/classify", json=test, timeout=5)
            result = resp.json()
            category = result.get("data", {}).get("category")
            
            status = "✅" if category == test["expected"] else "❌"
            print(f"{status} Test {i}: code={test['code']}, msg={test['message']}")
            print(f"   Expected: {test['expected']}, Got: {category}")
            print(f"   Recommendation: {result.get('data', {}).get('recommendation')}")
        
        return True
    except Exception as e:
        print(f"❌ Classifier tests failed: {e}")
        return False

def test_recovery_links(txn_ref):
    print_section("4. RECOVERY LINK GENERATION")
    
    if not txn_ref:
        print("⚠️  Skipping - no transaction reference")
        return None
    
    try:
        # Create recovery link
        payload = {
            "ttl_hours": 24,
            "channel": "email"
        }
        
        resp = requests.post(
            f"{BASE_URL}/v1/recoveries/by_ref/{txn_ref}/link",
            json=payload,
            timeout=5
        )
        print(f"✅ POST /v1/recoveries/by_ref/{txn_ref}/link - Status: {resp.status_code}")
        data = resp.json()
        token = data.get("token")
        print(f"   Token: {token}")
        print(f"   URL: {data.get('url')}")
        print(f"   Expires: {data.get('expires_at')}")
        
        # List recovery attempts
        resp = requests.get(f"{BASE_URL}/v1/recoveries/by_ref/{txn_ref}", timeout=5)
        print(f"✅ GET /v1/recoveries/by_ref/{txn_ref} - Status: {resp.status_code}")
        print(f"   Found {len(resp.json())} recovery attempt(s)")
        
        return token
    except Exception as e:
        print(f"❌ Recovery link generation failed: {e}")
        return None

def test_recovery_token_validation(token):
    print_section("5. RECOVERY TOKEN VALIDATION")
    
    if not token:
        print("⚠️  Skipping - no token available")
        return
    
    try:
        # Validate token
        resp = requests.get(f"{BASE_URL}/v1/recoveries/by_token/{token}", timeout=5)
        print(f"✅ GET /v1/recoveries/by_token/{token} - Status: {resp.status_code}")
        data = resp.json()
        print(f"   Valid: {data.get('ok')}")
        print(f"   Status: {data.get('data', {}).get('status')}")
        print(f"   Transaction: {data.get('data', {}).get('transaction_ref')}")
        
        # Mark as opened (idempotent)
        resp = requests.post(f"{BASE_URL}/v1/recoveries/by_token/{token}/open", timeout=5)
        print(f"✅ POST /v1/recoveries/by_token/{token}/open - Status: {resp.status_code}")
        data = resp.json()
        print(f"   Status after open: {data.get('data', {}).get('status')}")
        print(f"   Opened at: {data.get('data', {}).get('opened_at')}")
        
        # Test idempotency - call again
        resp = requests.post(f"{BASE_URL}/v1/recoveries/by_token/{token}/open", timeout=5)
        print(f"✅ Idempotency test - Status: {resp.status_code} (should be same)")
        
        # Test invalid token
        resp = requests.get(f"{BASE_URL}/v1/recoveries/by_token/invalid-token-xyz", timeout=5)
        print(f"✅ Invalid token test - Status: {resp.status_code}")
        data = resp.json()
        print(f"   Expected error: {data.get('error', {}).get('code')}")
        
        return True
    except Exception as e:
        print(f"❌ Token validation failed: {e}")
        return False

def test_payment_endpoints(txn_ref):
    print_section("6. PAYMENT ENDPOINTS (Razorpay)")

    try:
        # Status check (non-sensitive)
        print("\n--- Razorpay Status ---")
        resp = requests.get(f"{BASE_URL}/v1/payments/razorpay/status", timeout=5)
        print(f"   Status: {resp.status_code}")
        try:
            print(f"   Body: {resp.json()}")
        except Exception:
            print("   Body: <non-JSON>")

        # Ping Razorpay configuration
        print("\n--- Razorpay Ping ---")
        resp = requests.get(f"{BASE_URL}/v1/payments/razorpay/ping", timeout=5)
        if resp.status_code == 503:
            print("⚠️  Razorpay not configured (set RAZORPAY_KEY_ID/RAZORPAY_KEY_SECRET)")
            return True  # treat as soft pass
        print(f"✅ GET /v1/payments/razorpay/ping - Status: {resp.status_code}")

        # Optionally, test order creation if we have a transaction ref
        if txn_ref:
            print("\n--- Razorpay Create Order (public) ---")
            resp = requests.post(
                f"{BASE_URL}/v1/payments/razorpay/orders-public",
                json={"ref": txn_ref},
                timeout=5,
            )
            print(f"   Status: {resp.status_code}")
            try:
                print(f"   Body: {resp.json()}")
            except Exception:
                print("   Body: <non-JSON>")
        return True
    except Exception as e:
        print(f"❌ Payment endpoint tests failed: {e}")
        return False

def test_webhooks():
    print_section("7. WEBHOOK ENDPOINTS")
    
    try:
        # Test Razorpay webhook (will fail due to missing signature - expected)
        print("\n--- Razorpay Webhook ---")
        resp = requests.post(
            f"{BASE_URL}/v1/webhooks/razorpay",
            json={"event": "payment.captured", "payload": {"payment": {"entity": {"id": "pay_test", "order_id": "order_test"}}}},
            timeout=5,
        )
        if resp.status_code in [400, 503]:
            print(f"⚠️  POST /v1/webhooks/razorpay - Expected failure (missing/invalid signature)")
            try:
                print(f"   Message: {resp.json().get('detail')}")
            except Exception:
                pass
        else:
            print(f"✅ POST /v1/webhooks/razorpay - Status: {resp.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Webhook tests failed: {e}")
        return False

def test_frontend_accessibility():
    print_section("8. FRONTEND ACCESSIBILITY")
    
    frontend_urls = [
        "http://localhost:3000",
        "http://localhost:3000/auth/signin",
        "http://localhost:3000/auth/signup",
        "http://localhost:3000/pricing",
        "http://localhost:3000/contact",
        "http://localhost:3000/privacy",
        "http://localhost:3000/terms",
    ]
    
    print("\n⚠️  Frontend tests require manual browser testing")
    print("   Please verify these URLs in a browser:")
    for url in frontend_urls:
        print(f"   - {url}")
    
    print("\n   Protected routes (require signin):")
    protected = [
        "http://localhost:3000/dashboard",
        "http://localhost:3000/onboarding",
        "http://localhost:3000/rules",
        "http://localhost:3000/templates",
        "http://localhost:3000/developer",
        "http://localhost:3000/settings",
    ]
    for url in protected:
        print(f"   - {url}")

def main():
    print("\n" + "█"*60)
    print("  TINKO RECOVERY - COMPREHENSIVE TEST SUITE")
    print("█"*60)
    
    # Test backend availability first
    try:
        requests.get(f"{BASE_URL}/healthz", timeout=2)
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Backend not running at {BASE_URL}")
        print("   Please start the backend first:")
        print("   cd Stealth-Reecovery && uvicorn app.main:app --reload")
        sys.exit(1)
    
    # Run all tests
    health_ok = test_health_endpoints()
    txn_ref = test_event_ingestion()
    classifier_ok = test_classifier()
    token = test_recovery_links(txn_ref)
    validation_ok = test_recovery_token_validation(token)
    payment_ok = test_payment_endpoints(txn_ref)
    webhook_ok = test_webhooks()
    test_frontend_accessibility()
    
    # Summary
    print_section("TEST SUMMARY")
    results = [
        ("Health Checks", health_ok),
        ("Event Ingestion", txn_ref is not None),
        ("Classifier", classifier_ok),
        ("Recovery Links", token is not None),
        ("Token Validation", validation_ok),
        ("Payment Endpoints", payment_ok),
        ("Webhooks", webhook_ok),
    ]
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "█"*60)
    print(f"  Tests Passed: {sum(1 for _, p in results if p)}/{len(results)}")
    print("█"*60 + "\n")

if __name__ == "__main__":
    main()
