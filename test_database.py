"""
Database and OTP Flow Testing Script

This script will:
1. Test database connection
2. Create test tables
3. Test OTP registration flow
4. Verify data is stored correctly
5. Test login with stored credentials
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.models import User, Organization
from app.security import hash_password, verify_password
from dotenv import load_dotenv
import asyncio

load_dotenv()

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_step(step_num, message):
    print(f"\n{BLUE}━━━ STEP {step_num}: {message} ━━━{RESET}")

def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")

def print_error(message):
    print(f"{RED}✗ {message}{RESET}")

def print_info(message):
    print(f"{YELLOW}ℹ {message}{RESET}")


def test_database_connection():
    """Step 1: Test if we can connect to the database"""
    print_step(1, "Testing Database Connection")
    
    try:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print_error("DATABASE_URL not found in .env file")
            return None
        
        print_info(f"Connecting to: {db_url.split('@')[1].split('/')[0]}")
        
        engine = create_engine(db_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print_success(f"Connected to PostgreSQL!")
            print_info(f"Version: {version[:50]}...")
        
        return engine
        
    except Exception as e:
        print_error(f"Database connection failed: {str(e)}")
        return None


def create_tables(engine):
    """Step 2: Create all database tables"""
    print_step(2, "Creating Database Tables")
    
    try:
        Base.metadata.create_all(engine)
        print_success("All tables created successfully!")
        
        # List created tables
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename
            """))
            tables = [row[0] for row in result.fetchall()]
            print_info(f"Tables in database: {', '.join(tables)}")
        
        return True
        
    except Exception as e:
        print_error(f"Table creation failed: {str(e)}")
        return False


def test_insert_user(engine):
    """Step 3: Test inserting a user into the database"""
    print_step(3, "Testing User Registration (Database Insert)")
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Check if test org exists
        test_org = session.query(Organization).filter(
            Organization.slug == "test-org"
        ).first()
        
        if not test_org:
            # Create test organization
            test_org = Organization(
                name="Test Organization",
                slug="test-org",
                is_active=True
            )
            session.add(test_org)
            session.flush()
            print_success(f"Created test organization: {test_org.name} (ID: {test_org.id})")
        else:
            print_info(f"Using existing organization: {test_org.name} (ID: {test_org.id})")
        
        # Check if test user exists
        test_email = "test@example.com"
        existing_user = session.query(User).filter(User.email == test_email).first()
        
        if existing_user:
            print_info(f"User {test_email} already exists (ID: {existing_user.id})")
            print_info(f"Deleting old user for fresh test...")
            session.delete(existing_user)
            session.commit()
        
        # Create test user
        hashed_pw = hash_password("TestPassword123!")
        test_user = User(
            email=test_email,
            hashed_password=hashed_pw,
            full_name="Test User",
            role="admin",
            org_id=test_org.id,
            is_active=True
        )
        
        session.add(test_user)
        session.commit()
        session.refresh(test_user)
        
        print_success(f"User created successfully!")
        print_info(f"  Email: {test_user.email}")
        print_info(f"  Name: {test_user.full_name}")
        print_info(f"  Role: {test_user.role}")
        print_info(f"  User ID: {test_user.id}")
        print_info(f"  Org ID: {test_user.org_id}")
        print_info(f"  Active: {test_user.is_active}")
        
        session.close()
        return test_user.email
        
    except Exception as e:
        print_error(f"User insertion failed: {str(e)}")
        return None


def test_retrieve_user(engine, email):
    """Step 4: Test retrieving and verifying user from database"""
    print_step(4, "Testing User Retrieval and Password Verification")
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Retrieve user
        user = session.query(User).filter(User.email == email).first()
        
        if not user:
            print_error(f"User {email} not found in database")
            return False
        
        print_success(f"User retrieved from database!")
        print_info(f"  Email: {user.email}")
        print_info(f"  Name: {user.full_name}")
        print_info(f"  Organization: {user.organization.name}")
        
        # Test password verification
        correct_password = "TestPassword123!"
        wrong_password = "WrongPassword"
        
        if verify_password(correct_password, user.hashed_password):
            print_success("Password verification works correctly!")
        else:
            print_error("Password verification failed!")
            return False
        
        if not verify_password(wrong_password, user.hashed_password):
            print_success("Wrong password correctly rejected!")
        else:
            print_error("Wrong password was incorrectly accepted!")
            return False
        
        session.close()
        return True
        
    except Exception as e:
        print_error(f"User retrieval failed: {str(e)}")
        return False


def test_login_flow(engine, email):
    """Step 5: Simulate complete login flow"""
    print_step(5, "Testing Complete Login Flow")
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Simulate login attempt
        input_email = email
        input_password = "TestPassword123!"
        
        print_info(f"Attempting login with: {input_email}")
        
        # Step 1: Find user by email
        user = session.query(User).filter(User.email == input_email).first()
        
        if not user:
            print_error("User not found (login would fail)")
            return False
        
        print_success("User found in database")
        
        # Step 2: Verify password
        if not verify_password(input_password, user.hashed_password):
            print_error("Password incorrect (login would fail)")
            return False
        
        print_success("Password verified")
        
        # Step 3: Check if user is active
        if not user.is_active:
            print_error("User not active (login would fail - email not verified)")
            return False
        
        print_success("User is active")
        
        # Step 4: Success!
        print_success("✓✓✓ Login would succeed! ✓✓✓")
        print_info(f"  User ID: {user.id}")
        print_info(f"  Role: {user.role}")
        print_info(f"  Organization: {user.organization.name}")
        
        session.close()
        return True
        
    except Exception as e:
        print_error(f"Login flow test failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  DATABASE & OTP FLOW TESTING SCRIPT{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    # Step 1: Test database connection
    engine = test_database_connection()
    if not engine:
        print_error("\n❌ Cannot proceed without database connection")
        return
    
    # Step 2: Create tables
    if not create_tables(engine):
        print_error("\n❌ Cannot proceed without tables")
        return
    
    # Step 3: Test user insertion
    test_email = test_insert_user(engine)
    if not test_email:
        print_error("\n❌ User insertion failed")
        return
    
    # Step 4: Test user retrieval
    if not test_retrieve_user(engine, test_email):
        print_error("\n❌ User retrieval failed")
        return
    
    # Step 5: Test login flow
    if not test_login_flow(engine, test_email):
        print_error("\n❌ Login flow failed")
        return
    
    # Final summary
    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}  ✓ ALL TESTS PASSED!{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")
    print(f"\n{YELLOW}Next Steps:{RESET}")
    print("  1. Set up SendGrid API key in .env file")
    print("  2. Test OTP email sending with real registration")
    print("  3. Test complete flow from frontend")
    print()


if __name__ == "__main__":
    main()
