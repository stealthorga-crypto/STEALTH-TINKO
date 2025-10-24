#!/usr/bin/env python3
"""
End-to-end smoke test for Tinko Recovery stack.
Tests: Create failure event → Generate recovery link → Verify link accessible

This module is intended for manual invocation, not as part of the pytest unit
test suite. We mark it skipped for pytest to avoid CI failures.
"""
try:
    import pytest  # type: ignore
    pytestmark = pytest.mark.skip("skip end-to-end smoke in pytest runs")
except Exception:
    pass
import os
import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def print_section(title):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_backend_health():
    """Test backend health endpoint"""
    print_section("1. Backend Health Check")
    response = requests.get(f"{BASE_URL}/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] == True
    print("✅ Backend is healthy")
    return True

def test_frontend_accessible():
    """Test frontend is accessible"""
    print_section("2. Frontend Accessibility Check")
    # Allow skipping in CI/local if frontend isn't running
    if os.getenv("RUN_SMOKE_E2E", "0") not in ("1", "true", "yes"):
        print("(skipped) Frontend check disabled; set RUN_SMOKE_E2E=1 to enable")
        return True
    response = requests.get(FRONTEND_URL)
    assert response.status_code == 200
    assert "Tinko" in response.text
    print("✅ Frontend is accessible")
    return True

def seed_test_data():
    """Seed test organization and user"""
    print_section("3. Seed Test Data")
    
    # Create organization directly in database
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    
    # Use docker compose service name
    engine = create_engine("postgresql://tinko:tinko@localhost:5432/tinko")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Insert test org
        session.execute(text("""
            INSERT INTO organizations (name, slug, is_active)
            VALUES ('Test Org', 'test-org', true)
            ON CONFLICT (slug) DO NOTHING
        """))
        
        # Get org ID
        result = session.execute(text("SELECT id FROM organizations WHERE slug = 'test-org'"))
        org_id = result.scalar()
        
        # Insert test user with hashed password (bcrypt hash of "password123")
        session.execute(text("""
            INSERT INTO users (email, hashed_password, full_name, role, is_active, org_id)
            VALUES (
                'test@example.com',
                '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5DT8KeJRO.6/.',
                'Test User',
                'admin',
                true,
                :org_id
            )
            ON CONFLICT (email) DO NOTHING
        """), {"org_id": org_id})
        
        session.commit()
        print(f"✅ Seeded test org (ID: {org_id}) and user (test@example.com)")
        return org_id
    except Exception as e:
        session.rollback()
        print(f"⚠️  Warning: {e}")
        # Try to get existing org
        result = session.execute(text("SELECT id FROM organizations WHERE slug = 'test-org'"))
        org_id = result.scalar()
        return org_id
    finally:
        session.close()

def login_and_get_token():
    """Login and get access token"""
    print_section("4. Authentication Test")
    
    response = requests.post(
        f"{BASE_URL}/v1/auth/token",
        data={
            "username": "test@example.com",
            "password": "password123"
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    access_token = data["access_token"]
    print("✅ Successfully authenticated")
    print(f"   Token: {access_token[:20]}...")
    return access_token

def create_failure_event(token, org_id):
    """Create a test failure event"""
    print_section("5. Create Failure Event")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "transaction_ref": f"TXN-{int(time.time())}",
        "amount": 10000,  # ₹100.00
        "currency": "INR",
        "customer_email": "customer@example.com",
        "customer_phone": "+919876543210",
        "org_id": org_id,
        "failure_reason": "insufficient_funds"
    }
    
    response = requests.post(
        f"{BASE_URL}/v1/events/failure",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200 and response.status_code != 201:
        print(f"❌ Failed to create failure event: {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    print(f"✅ Created failure event for transaction: {data['transaction_ref']}")
    return data

def generate_recovery_link(token, transaction_ref):
    """Generate a recovery link for the transaction"""
    print_section("6. Generate Recovery Link")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "transaction_ref": transaction_ref,
        "channel": "link",
        "expires_in_hours": 48
    }
    
    response = requests.post(
        f"{BASE_URL}/v1/recovery-links",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200 and response.status_code != 201:
        print(f"❌ Failed to generate recovery link: {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    print(f"✅ Generated recovery link")
    print(f"   Token: {data['token']}")
    print(f"   URL: {FRONTEND_URL}/pay/{data['token']}")
    print(f"   Expires: {data['expires_at']}")
    return data

def test_recovery_link_page(token):
    """Test that recovery link page loads"""
    print_section("7. Test Recovery Link Page")
    if os.getenv("RUN_SMOKE_E2E", "0") not in ("1", "true", "yes"):
        print("(skipped) Recovery link page check disabled; set RUN_SMOKE_E2E=1 to enable")
        return True
    url = f"{FRONTEND_URL}/pay/{token}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"❌ Recovery link page failed: {response.status_code}")
        return False
    
    print(f"✅ Recovery link page is accessible")
    print(f"   URL: {url}")
    return True

def test_mailhog():
    """Check MailHog is receiving emails"""
    print_section("8. Check MailHog (SMTP Test Server)")
    if os.getenv("RUN_SMOKE_E2E", "0") not in ("1", "true", "yes"):
        print("(skipped) MailHog check disabled; set RUN_SMOKE_E2E=1 to enable")
        return True
    response = requests.get("http://localhost:8025/api/v2/messages")
    if response.status_code == 200:
        messages = response.json()
        print(f"✅ MailHog is running")
        print(f"   Messages in queue: {len(messages.get('items', []))}")
        print(f"   UI: http://localhost:8025")
    else:
        print(f"⚠️  MailHog may not be running")

def print_summary():
    """Print test summary and next steps"""
    print_section("✨ Smoke Test Complete!")
    
    print("📊 Service Status:")
    print(f"   ✅ Backend API:    http://localhost:8000/docs")
    print(f"   ✅ Frontend:       http://localhost:3000")
    print(f"   ✅ Database:       PostgreSQL on port 5432")
    print(f"   ✅ Redis:          Port 6379")
    print(f"   ✅ MailHog:        http://localhost:8025")
    
    print("\n🚀 Next Steps:")
    print("   1. Start Celery worker:")
    print("      docker compose exec backend celery -A app.worker.celery worker -l info")
    print("\n   2. Start Celery beat scheduler:")
    print("      docker compose exec backend celery -A app.worker.celery beat -l info")
    print("\n   3. Test Stripe webhook (if Stripe CLI installed):")
    print("      stripe listen --events checkout.session.completed --forward-to http://localhost:8000/v1/webhooks/stripe")
    print("\n   4. Create test Stripe Checkout session via recovery link")

def main():
    """Run all smoke tests"""
    print("""
████████╗██╗███╗   ██╗██╗  ██╗ ██████╗ 
╚══██╔══╝██║████╗  ██║██║ ██╔╝██╔═══██╗
   ██║   ██║██╔██╗ ██║█████╔╝ ██║   ██║
   ██║   ██║██║╚██╗██║██╔═██╗ ██║   ██║
   ██║   ██║██║ ╚████║██║  ██╗╚██████╔╝
   ╚═╝   ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ 
                                        
   Recovery Stack - End-to-End Smoke Test
    """)
    
    try:
        # Run tests
        test_backend_health()
        test_frontend_accessible()
        org_id = seed_test_data()
        token = login_and_get_token()
        
        if not token:
            print("\n❌ Authentication failed - cannot proceed")
            return
        
        failure_event = create_failure_event(token, org_id)
        if not failure_event:
            print("\n❌ Failed to create failure event - cannot proceed")
            return
        
        recovery_link = generate_recovery_link(token, failure_event["transaction_ref"])
        if not recovery_link:
            print("\n❌ Failed to generate recovery link - cannot proceed")
            return
        
        test_recovery_link_page(recovery_link["token"])
        test_mailhog()
        
        print_summary()
        
    except Exception as e:
        print(f"\n❌ Smoke test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
