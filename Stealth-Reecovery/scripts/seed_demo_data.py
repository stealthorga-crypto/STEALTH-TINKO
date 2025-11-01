"""
Seed script to populate database with demo data for testing.

Creates realistic sample data including:
- Organizations
- Users
- Failed payments with various failure reasons
- Recovery events
- Payment status updates
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal, engine, Base
from app.models import (
    Organization, User, Transaction, FailureEvent, RecoveryAttempt
)
from app.security import hash_password
from sqlalchemy import func

# Demo data constants
FAILURE_REASONS = [
    "insufficient_funds",
    "card_declined",
    "expired_card",
    "invalid_card",
    "payment_method_unavailable",
    "authentication_required",
    "processing_error",
]

RECOVERY_CHANNELS = ["email", "sms", "payment_link", "automated_retry"]

def create_demo_org_and_user(db):
    """Create demo organization and admin user."""
    # Check if demo org already exists
    org = db.query(Organization).filter(Organization.slug == "demo-org").first()
    if org:
        print("✓ Demo organization already exists")
        user = db.query(User).filter(User.org_id == org.id).first()
        return org, user
    
    # Create organization
    org = Organization(
        name="Demo Company",
        slug="demo-org",
        is_active=True
    )
    db.add(org)
    db.flush()
    
    # Create admin user
    user = User(
        email="demo@example.com",
        hashed_password=hash_password("demo123"),
        full_name="Demo Admin",
        role="admin",
        is_active=True,
        org_id=org.id
    )
    db.add(user)
    db.commit()
    
    print(f"✓ Created organization: {org.name}")
    print(f"✓ Created user: {user.email} (password: demo123)")
    
    return org, user


def create_failed_payments(db, org_id, count=50):
    """Create transactions with failure events."""
    print(f"\nCreating {count} failed transactions...")
    
    base_time = datetime.utcnow() - timedelta(days=30)
    transactions = []
    
    for i in range(count):
        # Random time within last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        event_time = base_time + timedelta(days=days_ago, hours=hours_ago)
        
        # Random amount between $10 and $500
        amount = random.randint(1000, 50000)  # in cents
        
        # Random failure reason
        failure_reason = random.choice(FAILURE_REASONS)
        
        # Create transaction reference
        transaction_ref = f"tx_{org_id}_{i+1:04d}"
        
        # Create transaction
        transaction = Transaction(
            transaction_ref=transaction_ref,
            amount=amount,
            currency="usd",
            org_id=org_id,
            customer_email=f"customer{i+1}@example.com",
            customer_phone=f"+1555{random.randint(1000000, 9999999)}",
            stripe_payment_intent_id=f"pi_demo_{random.randint(100000, 999999)}",
            created_at=event_time,
            updated_at=event_time
        )
        db.add(transaction)
        db.flush()
        
        # Create failure event for this transaction
        failure = FailureEvent(
            transaction_id=transaction.id,
            gateway="stripe",
            reason=failure_reason,
            meta={"demo": True, "amount": amount},
            occurred_at=event_time,
            created_at=event_time
        )
        db.add(failure)
        transactions.append(transaction)
    
    db.commit()
    print(f"✓ Created {count} transactions with failure events")
    return transactions


def create_recovery_events(db, transactions, recovery_rate=0.35):
    """Create recovery attempts for a percentage of failed transactions."""
    # Determine how many to recover
    num_to_recover = int(len(transactions) * recovery_rate)
    transactions_to_recover = random.sample(transactions, num_to_recover)
    
    print(f"\nCreating {num_to_recover} recovery attempts ({recovery_rate*100}% recovery rate)...")
    
    for transaction in transactions_to_recover:
        # Recovery happens 1-10 days after failure
        days_later = random.randint(1, 10)
        recovery_time = transaction.created_at + timedelta(days=days_later)
        
        # Create recovery attempt
        channel = random.choice(RECOVERY_CHANNELS)
        
        # Generate token
        import secrets
        token = secrets.token_urlsafe(32)
        
        # Determine if completed
        is_completed = random.random() < 0.8  # 80% of recovery attempts succeed
        status = "completed" if is_completed else "sent"
        
        recovery = RecoveryAttempt(
            transaction_id=transaction.id,
            transaction_ref=transaction.transaction_ref,
            channel=channel,
            token=token,
            status=status,
            expires_at=recovery_time + timedelta(days=7),
            opened_at=recovery_time + timedelta(hours=2) if is_completed else None,
            used_at=recovery_time + timedelta(hours=3) if is_completed else None,
            created_at=recovery_time,
            retry_count=random.randint(0, 2),
            max_retries=3
        )
        db.add(recovery)
    
    db.commit()
    print(f"✓ Created {num_to_recover} recovery attempts")


def print_summary(db, org_id):
    """Print summary of created data."""
    # Count transactions
    failed_count = db.query(Transaction).filter(
        Transaction.org_id == org_id
    ).count()
    
    # Count recovery attempts
    recovery_count = db.query(RecoveryAttempt).filter(
        RecoveryAttempt.status == "completed"
    ).join(Transaction).filter(
        Transaction.org_id == org_id
    ).count()
    
    # Sum amounts
    total_failed = db.query(func.sum(Transaction.amount)).filter(
        Transaction.org_id == org_id
    ).scalar() or 0
    
    # Get completed recoveries amount
    total_recovered = db.query(func.sum(Transaction.amount)).join(RecoveryAttempt).filter(
        Transaction.org_id == org_id,
        RecoveryAttempt.status == "completed"
    ).scalar() or 0
    
    recovery_rate = (recovery_count / failed_count * 100) if failed_count > 0 else 0
    
    print("\n" + "="*60)
    print("DEMO DATA SUMMARY")
    print("="*60)
    print(f"Failed Transactions: {failed_count}")
    print(f"Recovered Payments:  {recovery_count}")
    print(f"Recovery Rate:       {recovery_rate:.1f}%")
    print(f"Total Failed:        ${total_failed/100:,.2f}")
    print(f"Total Recovered:     ${total_recovered/100:,.2f}")
    print(f"Pending Recovery:    ${(total_failed - total_recovered)/100:,.2f}")
    print("="*60)
    print("\n✅ Demo data seed complete!")
    print("\nYou can now:")
    print("  1. View dashboard at http://localhost:3000/dashboard")
    print("  2. Test API at http://127.0.0.1:8000/docs")
    print("  3. Login with: demo@example.com / demo123")
    print()


def create_stripe_webhooks(db, org_id, count=10):
    """Create sample webhook logs (simplified - just for demonstration)."""
    print(f"\nNote: Skipping Stripe webhook creation (not in current schema)")
    print(f"      Webhook handling is integrated with real Stripe events")


def main():
    """Main seed function."""
    print("="*60)
    print("DEMO DATA SEED SCRIPT")
    print("="*60)
    
    # Create tables if they don't exist
    print("\nInitializing database...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables ready")
    
    db = SessionLocal()
    try:
        # Create org and user
        org, user = create_demo_org_and_user(db)
        
        # Create failed transactions
        transactions = create_failed_payments(db, org.id, count=50)
        
        # Create recoveries (35% recovery rate)
        create_recovery_events(db, transactions, recovery_rate=0.35)
        
        # Note about webhooks
        create_stripe_webhooks(db, org.id, count=20)
        
        # Print summary
        print_summary(db, org.id)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
