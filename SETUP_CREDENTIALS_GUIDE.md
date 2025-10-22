# 🔐 TINKO RECOVERY PLATFORM - COMPLETE SETUP CREDENTIALS GUIDE

**Generated:** October 21, 2025  
**Purpose:** Step-by-step guide to obtain ALL required credentials, keys, and IDs  
**Status:** Production-Ready Configuration

---

## 📋 TABLE OF CONTENTS

1. [Quick Overview](#quick-overview)
2. [Core Application Setup](#core-application-setup)
3. [Database Configuration](#database-configuration)
4. [Authentication & Security](#authentication--security)
5. [Payment Gateway Setup](#payment-gateway-setup)
6. [Notification Services](#notification-services)
7. [Background Workers](#background-workers)
8. [Monitoring & Observability](#monitoring--observability)
9. [Frontend Configuration](#frontend-configuration)
10. [Complete .env File Template](#complete-env-file-template)
11. [Verification Checklist](#verification-checklist)

---

## 🎯 QUICK OVERVIEW

### Required Services (Minimum to Run)

- ✅ **Database** (PostgreSQL or SQLite) - FREE
- ✅ **Redis** (for Celery) - FREE
- ✅ **Stripe** (Payment Gateway) - FREE Test Mode
- ⚠️ **Email Service** (SMTP) - FREE (Gmail)
- ⚠️ **Sentry** (Error Tracking) - FREE Tier

### Optional Services (Enhanced Features)

- 🔵 **Razorpay** (Indian Payments) - Requires Business Account
- 🔵 **Twilio** (SMS) - $15 Free Trial Credit
- 🔵 **WhatsApp Business API** - Requires Approval
- 🔵 **ClickHouse** (Analytics) - Self-hosted or Cloud

### Total Setup Time

- **Minimum Setup:** 30-45 minutes
- **Full Setup:** 2-3 hours

---

## 🗄️ CORE APPLICATION SETUP

### 1. Project Directory Structure

**Location:** Your local machine or server

**Setup:**

```bash
# Clone repository
git clone https://github.com/stealthorga-crypto/STEALTH-TINKO.git
cd STEALTH-TINKO/Stealth-Reecovery

# Or if already cloned
cd /c/Users/srina/OneDrive/Documents/Downloads/Stealth-Reecovery-20251010T154256Z-1-001/Stealth-Reecovery
```

**Required Files:**

- `.env` (create in root directory)
- `tinko-console/.env.local` (create in frontend directory)

---

## 💾 DATABASE CONFIGURATION

### Option A: SQLite (Development - Easiest)

**Cost:** FREE  
**Setup Time:** 0 minutes (automatic)  
**Recommended For:** Local development, testing

**Configuration:**

```env
DATABASE_URL=sqlite:///./recovery.db
```

**No additional setup required!** SQLite file will be created automatically.

---

### Option B: PostgreSQL (Production - Recommended)

**Cost:** FREE to $7/month  
**Setup Time:** 15 minutes  
**Recommended For:** Production, staging

#### Local PostgreSQL (Docker)

```bash
# Start PostgreSQL container
docker run -d \
  --name tinko-postgres \
  -e POSTGRES_USER=tinko \
  -e POSTGRES_PASSWORD=tinko_secure_pass_123 \
  -e POSTGRES_DB=tinko_recovery \
  -p 5432:5432 \
  postgres:15-alpine

# Verify it's running
docker ps | grep tinko-postgres
```

**Configuration:**

```env
DATABASE_URL=postgresql://tinko:tinko_secure_pass_123@localhost:5432/tinko_recovery
```

#### Cloud PostgreSQL Options

##### 1. **Supabase** (Recommended - FREE tier)

- **Website:** https://supabase.com/
- **Free Tier:** 500MB database, 2GB bandwidth/month
- **Setup Steps:**
  1. Sign up at https://supabase.com/dashboard
  2. Create new project (choose region close to users)
  3. Wait 2 minutes for provisioning
  4. Go to Settings → Database
  5. Copy "Connection string" under "Connection pooling"
  6. Replace `[YOUR-PASSWORD]` with your actual password

**Configuration:**

```env
DATABASE_URL=postgresql://postgres.xxxxxxxxxxxx:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

##### 2. **Neon** (Serverless PostgreSQL)

- **Website:** https://neon.tech/
- **Free Tier:** 3GB storage, 10 projects
- **Setup Steps:**
  1. Sign up at https://console.neon.tech/
  2. Create new project
  3. Copy connection string from dashboard

**Configuration:**

```env
DATABASE_URL=postgresql://user:password@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb
```

##### 3. **Railway** (Easy Deploy)

- **Website:** https://railway.app/
- **Free Tier:** $5 credit/month
- **Setup Steps:**
  1. Sign up at https://railway.app/
  2. New Project → Add PostgreSQL
  3. Copy DATABASE_URL from Variables tab

**Configuration:**

```env
DATABASE_URL=postgresql://postgres:password@containers-us-west-1.railway.app:5432/railway
```

##### 4. **Amazon RDS** (Enterprise)

- **Website:** https://aws.amazon.com/rds/
- **Cost:** ~$15-30/month (db.t3.micro)
- **Setup Steps:**
  1. AWS Console → RDS → Create database
  2. Choose PostgreSQL 15
  3. Template: Free tier or Production
  4. Set master username/password
  5. Public access: Yes (for development)
  6. Note endpoint after creation

**Configuration:**

```env
DATABASE_URL=postgresql://admin:your_password@tinko-db.xxxxxxxxxx.us-east-1.rds.amazonaws.com:5432/tinko
```

---

## 🔐 AUTHENTICATION & SECURITY

### 1. JWT Secret Key

**Cost:** FREE  
**Setup Time:** 1 minute

**Generate Strong Secret:**

```bash
# Option 1: Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Option 2: Using OpenSSL
openssl rand -base64 32

# Option 3: Online Generator (use only for development)
# https://randomkeygen.com/
```

**Configuration:**

```env
JWT_SECRET=your_generated_secret_here_32_chars_minimum
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=30
```

**Example:**

```env
JWT_SECRET=k7j9m2n4p6q8r1s3t5u7v9w0x2y4z6a8b0c2d4e6f8g0
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=30
```

---

### 2. NextAuth Secret (Frontend)

**Cost:** FREE  
**Setup Time:** 1 minute

**Generate:**

```bash
# Option 1: Using OpenSSL
openssl rand -base64 32

# Option 2: Using Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

**Configuration (Frontend):**

```env
# tinko-console/.env.local
NEXTAUTH_SECRET=your_nextauth_secret_here
NEXTAUTH_URL=http://localhost:3000
```

---

## 💳 PAYMENT GATEWAY SETUP

### 1. Stripe (Primary - International)

**Cost:** FREE (Test mode), 2.9% + $0.30 per transaction (Live)  
**Setup Time:** 10 minutes  
**Website:** https://stripe.com/

#### Step-by-Step Setup:

**1. Create Stripe Account**

- Go to https://dashboard.stripe.com/register
- Sign up with email
- Verify email address
- Complete business profile (can skip for testing)

**2. Get API Keys**

- Dashboard → Developers → API keys
- **Test Mode Toggle:** Make sure you're in TEST mode (toggle in top right)
- Copy both keys:
  - **Publishable key:** Starts with `pk_test_`
  - **Secret key:** Starts with `sk_test_` (click "Reveal test key")

**3. Get Webhook Secret**

- Dashboard → Developers → Webhooks
- Click "Add endpoint"
- Endpoint URL: `http://localhost:8000/v1/webhooks/stripe` (for local dev)
- For production: `https://api.yourdomain.com/v1/webhooks/stripe`
- Select events to listen to:
  - ✅ `checkout.session.completed`
  - ✅ `payment_intent.succeeded`
  - ✅ `payment_intent.payment_failed`
  - ✅ `charge.refunded`
- Click "Add endpoint"
- Copy "Signing secret" (starts with `whsec_`)

**Configuration:**

```env
# Backend (.env)
STRIPE_SECRET_KEY=sk_test_51xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Frontend (tinko-console/.env.local)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_51xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Test the Integration:**

```bash
# Install Stripe CLI (optional but recommended)
# Windows: scoop install stripe
# Mac: brew install stripe/stripe-cli/stripe
# Linux: Download from https://github.com/stripe/stripe-cli/releases

# Login to Stripe
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:8000/v1/webhooks/stripe

# Use test card numbers (Stripe provides these)
# Success: 4242 4242 4242 4242
# Decline: 4000 0000 0000 0002
# Authentication Required: 4000 0025 0000 3155
```

---

### 2. Razorpay (Indian Market)

**Cost:** FREE (Test mode), 2% per transaction (Live)  
**Setup Time:** 15 minutes  
**Website:** https://razorpay.com/  
**Required:** Indian business/GST registration (for live mode)

#### Step-by-Step Setup:

**1. Create Razorpay Account**

- Go to https://dashboard.razorpay.com/signup
- Sign up with email and mobile number
- Verify OTP
- Complete KYC (for test mode, basic details enough)

**2. Get API Keys**

- Dashboard → Settings → API Keys
- Click "Generate Test Key" or "Generate Live Key"
- Copy both:
  - **Key ID:** Starts with `rzp_test_` or `rzp_live_`
  - **Key Secret:** Click "Show" to reveal

**3. Setup Webhooks**

- Dashboard → Settings → Webhooks
- Click "Add New Webhook"
- Webhook URL: `http://localhost:8000/v1/webhooks/razorpay` (local)
- Or: `https://api.yourdomain.com/v1/webhooks/razorpay` (production)
- Secret: Create your own (random string, save it)
- Active Events:
  - ✅ `payment.authorized`
  - ✅ `payment.captured`
  - ✅ `payment.failed`
  - ✅ `order.paid`
  - ✅ `refund.created`

**Configuration:**

```env
# Backend (.env)
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
RAZORPAY_WEBHOOK_SECRET=your_random_webhook_secret_123

# Frontend (tinko-console/.env.local)
NEXT_PUBLIC_RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxxxxx
```

**Install Razorpay SDK:**

```bash
cd Stealth-Reecovery
pip install razorpay
```

**Test the Integration:**

```bash
# Use test card numbers (Razorpay provides these)
# Success: 4111 1111 1111 1111
# OTP Failure: 5104 0600 0000 0008
# CVV: Any 3 digits
# Expiry: Any future date
```

---

### 3. PayU (Optional - India, Poland, UAE)

**Cost:** Varies by country  
**Website:** https://payu.in/ (India) or https://www.payu.com/  
**Status:** Adapter not implemented yet

**Future Configuration:**

```env
PAYU_MERCHANT_ID=your_merchant_id
PAYU_MERCHANT_KEY=your_merchant_key
PAYU_WEBHOOK_SECRET=your_webhook_secret
```

---

### 4. Cashfree (Optional - India)

**Cost:** 2% per transaction  
**Website:** https://www.cashfree.com/  
**Status:** Adapter not implemented yet

**Future Configuration:**

```env
CASHFREE_APP_ID=your_app_id
CASHFREE_SECRET_KEY=your_secret_key
CASHFREE_WEBHOOK_SECRET=your_webhook_secret
```

---

## 📧 NOTIFICATION SERVICES

### 1. Email Service (SMTP)

#### Option A: Gmail (Easiest for Development)

**Cost:** FREE  
**Setup Time:** 5 minutes  
**Limitations:** 500 emails/day

**Setup Steps:**

1. **Enable 2-Factor Authentication**

   - Go to https://myaccount.google.com/security
   - Click "2-Step Verification"
   - Follow setup wizard

2. **Generate App Password**
   - Go to https://myaccount.google.com/apppasswords
   - Select app: Mail
   - Select device: Other (Custom name)
   - Type: "Tinko Recovery Platform"
   - Click "Generate"
   - Copy the 16-character password (spaces are optional)

**Configuration:**

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your.email@gmail.com
SMTP_PASS=abcd efgh ijkl mnop
FROM_EMAIL=your.email@gmail.com
FROM_NAME=Tinko Recovery
```

**Test Email:**

```bash
cd Stealth-Reecovery
python -c "
from app.services.email_service import email_service
success = email_service.send_email(
    to_email='test@example.com',
    subject='Test Email',
    html_content='<h1>It works!</h1>',
    text_content='It works!'
)
print('Email sent!' if success else 'Failed!')
"
```

---

#### Option B: SendGrid (Production Recommended)

**Cost:** FREE (100 emails/day), $19.95/month (40k emails)  
**Setup Time:** 10 minutes  
**Website:** https://sendgrid.com/

**Setup Steps:**

1. Sign up at https://signup.sendgrid.com/
2. Verify email address
3. Create sender identity: Settings → Sender Authentication
4. Create API key:
   - Settings → API Keys
   - Create API Key
   - Name: "Tinko Production"
   - Permissions: Full Access (or Mail Send only)
   - Copy API key (starts with `SG.`)

**Configuration:**

```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASS=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=Tinko Recovery
```

---

#### Option C: AWS SES (Cheapest for High Volume)

**Cost:** $0.10 per 1,000 emails  
**Setup Time:** 20 minutes  
**Website:** https://aws.amazon.com/ses/

**Setup Steps:**

1. AWS Console → Simple Email Service
2. Verify email address or domain
3. Request production access (initially in sandbox mode)
4. Create SMTP credentials:
   - SMTP Settings → Create My SMTP Credentials
   - Download credentials file

**Configuration:**

```env
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=your_smtp_username
SMTP_PASS=your_smtp_password
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=Tinko Recovery
```

---

### 2. SMS Service (Twilio)

**Cost:** FREE ($15 trial credit), then $0.0075 per SMS (India)  
**Setup Time:** 10 minutes  
**Website:** https://www.twilio.com/

#### Setup Steps:

**1. Create Twilio Account**

- Go to https://www.twilio.com/try-twilio
- Sign up with email
- Verify phone number (they'll send you an SMS)
- Get $15 free trial credit

**2. Get Credentials**

- Dashboard: https://console.twilio.com/
- Copy these values:
  - **Account SID:** Starts with `AC`
  - **Auth Token:** Click to reveal

**3. Get Phone Number**

- Console → Phone Numbers → Buy a number
- For trial: You get one free number
- Choose a number from dropdown
- For India: Select Indian number (+91)

**4. Verify Test Numbers (Trial Mode)**

- Console → Phone Numbers → Verified Caller IDs
- Add phone numbers you want to test with
- Each number needs OTP verification

**Configuration:**

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_PHONE=+1234567890
```

**For India:**

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_PHONE=+91xxxxxxxxxx
```

**Test SMS:**

```bash
cd Stealth-Reecovery
python -c "
from app.services.sms_service import sms_service
success = sms_service.send_sms(
    to_phone='+1234567890',
    message='Test SMS from Tinko!'
)
print('SMS sent!' if success else 'Failed!')
"
```

---

### 3. WhatsApp Business (Optional)

**Cost:** $0.005-0.09 per message (varies by country)  
**Setup Time:** 1-2 weeks (requires approval)  
**Website:** https://www.twilio.com/whatsapp

**Setup Steps:**

1. Request access from Twilio
2. Complete WhatsApp Business Profile
3. Wait for Facebook approval (1-2 weeks)
4. Get WhatsApp-enabled number

**Configuration:**

```env
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

**Status:** Not implemented yet (future feature)

---

## ⚙️ BACKGROUND WORKERS

### 1. Redis (Required for Celery)

**Cost:** FREE  
**Setup Time:** 2 minutes

#### Option A: Docker (Recommended)

```bash
# Start Redis container
docker run -d \
  --name tinko-redis \
  -p 6379:6379 \
  --restart unless-stopped \
  redis:alpine

# Verify it's running
docker ps | grep tinko-redis

# Test connection
docker exec tinko-redis redis-cli ping
# Should return: PONG
```

**Configuration:**

```env
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

---

#### Option B: Cloud Redis

##### Upstash (Serverless Redis - FREE tier)

- **Website:** https://upstash.com/
- **Free Tier:** 10k commands/day, 256MB
- **Setup:**
  1. Sign up at https://console.upstash.com/
  2. Create database
  3. Copy "Redis URL"

**Configuration:**

```env
REDIS_URL=redis://default:your_password@us1-happy-fish-12345.upstash.io:6379
CELERY_BROKER_URL=redis://default:your_password@us1-happy-fish-12345.upstash.io:6379
CELERY_RESULT_BACKEND=redis://default:your_password@us1-happy-fish-12345.upstash.io:6379
```

##### Redis Labs (Cloud Redis)

- **Website:** https://redis.com/try-free/
- **Free Tier:** 30MB
- Similar setup to Upstash

---

### 2. Celery Configuration

**No additional keys needed!** Just install dependencies:

```bash
cd Stealth-Reecovery
pip install celery redis
```

**Start Workers:**

```bash
# Terminal 1: Celery Worker
celery -A app.worker worker --loglevel=info --pool=solo

# Terminal 2: Celery Beat (Scheduler)
celery -A app.worker beat --loglevel=info
```

---

## 📊 MONITORING & OBSERVABILITY

### 1. Sentry (Error Tracking)

**Cost:** FREE (5k events/month), $26/month (50k events)  
**Setup Time:** 5 minutes  
**Website:** https://sentry.io/

#### Setup Steps:

**1. Create Sentry Account**

- Go to https://sentry.io/signup/
- Sign up with GitHub or Email

**2. Create Project**

- Choose platform: Python (for backend) and Next.js (for frontend)
- Name: "Tinko Recovery Backend" and "Tinko Recovery Frontend"
- Copy the DSN (Data Source Name) after creation

**3. Get DSN**

- Dashboard → Settings → Projects → [Your Project] → Client Keys (DSN)
- Copy DSN (looks like: `https://abc123@o123456.ingest.sentry.io/7890123`)

**Configuration:**

```env
# Backend (.env)
SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
SENTRY_ENVIRONMENT=development

# Frontend (tinko-console/.env.local)
NEXT_PUBLIC_SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
NEXT_PUBLIC_SENTRY_ENVIRONMENT=development
```

**Test Sentry:**

```python
# Backend test
cd Stealth-Reecovery
python -c "
import sentry_sdk
sentry_sdk.init('your_dsn_here')
sentry_sdk.capture_message('Test from Tinko!')
print('Check Sentry dashboard!')
"
```

---

### 2. Logging Configuration

**Cost:** FREE  
**No external service needed**

**Configuration:**

```env
LOG_LEVEL=INFO
LOG_FORMAT=json
```

**Options:**

- `DEBUG` - Very verbose (development only)
- `INFO` - Standard (recommended)
- `WARNING` - Only warnings and errors
- `ERROR` - Only errors
- `CRITICAL` - Only critical errors

---

## 🌐 FRONTEND CONFIGURATION

### Frontend Environment Variables

**File:** `tinko-console/.env.local`

**Configuration:**

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Authentication
NEXTAUTH_SECRET=your_nextauth_secret_32_chars_min
NEXTAUTH_URL=http://localhost:3000

# Stripe
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx

# Razorpay (if using)
NEXT_PUBLIC_RAZORPAY_KEY_ID=rzp_test_xxxxx

# Sentry
NEXT_PUBLIC_SENTRY_DSN=https://xxx@sentry.io/xxx
NEXT_PUBLIC_SENTRY_ENVIRONMENT=development

# Feature Flags (optional)
NEXT_PUBLIC_ENABLE_RAZORPAY=false
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_NOTIFICATIONS=true
```

---

## 📝 COMPLETE .ENV FILE TEMPLATE

### Backend `.env` File

Create this file: `Stealth-Reecovery/.env`

```env
# =============================================================================
# TINKO RECOVERY PLATFORM - BACKEND CONFIGURATION
# =============================================================================
# Generated: October 21, 2025
# Environment: development
# =============================================================================

# -----------------------------------------------------------------------------
# APPLICATION SETTINGS
# -----------------------------------------------------------------------------
APP_NAME=Tinko Recovery
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO

# -----------------------------------------------------------------------------
# DATABASE CONFIGURATION
# -----------------------------------------------------------------------------
# Option 1: SQLite (Development)
DATABASE_URL=sqlite:///./recovery.db

# Option 2: PostgreSQL (Production) - UNCOMMENT TO USE
# DATABASE_URL=postgresql://user:password@localhost:5432/tinko_recovery

# Option 3: Cloud PostgreSQL (Supabase/Neon/Railway) - UNCOMMENT TO USE
# DATABASE_URL=postgresql://postgres:password@host.supabase.co:5432/postgres

# -----------------------------------------------------------------------------
# REDIS & CELERY (Background Tasks)
# -----------------------------------------------------------------------------
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# -----------------------------------------------------------------------------
# AUTHENTICATION & SECURITY
# -----------------------------------------------------------------------------
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET=CHANGE_THIS_TO_RANDOM_32_CHAR_STRING
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=30

# Password hashing
BCRYPT_ROUNDS=12

# -----------------------------------------------------------------------------
# STRIPE PAYMENT GATEWAY (PRIMARY)
# -----------------------------------------------------------------------------
# Get from: https://dashboard.stripe.com/apikeys
STRIPE_SECRET_KEY=sk_test_51xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# -----------------------------------------------------------------------------
# RAZORPAY PAYMENT GATEWAY (INDIA)
# -----------------------------------------------------------------------------
# Get from: https://dashboard.razorpay.com/app/keys
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
RAZORPAY_WEBHOOK_SECRET=your_random_webhook_secret_123

# -----------------------------------------------------------------------------
# EMAIL CONFIGURATION (SMTP)
# -----------------------------------------------------------------------------
# Option 1: Gmail - Get app password from https://myaccount.google.com/apppasswords
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your.email@gmail.com
SMTP_PASS=abcd efgh ijkl mnop
FROM_EMAIL=your.email@gmail.com
FROM_NAME=Tinko Recovery

# Option 2: SendGrid - UNCOMMENT TO USE
# SMTP_HOST=smtp.sendgrid.net
# SMTP_PORT=587
# SMTP_USER=apikey
# SMTP_PASS=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# FROM_EMAIL=noreply@yourdomain.com
# FROM_NAME=Tinko Recovery

# Option 3: AWS SES - UNCOMMENT TO USE
# SMTP_HOST=email-smtp.us-east-1.amazonaws.com
# SMTP_PORT=587
# SMTP_USER=your_aws_smtp_username
# SMTP_PASS=your_aws_smtp_password
# FROM_EMAIL=noreply@yourdomain.com
# FROM_NAME=Tinko Recovery

# -----------------------------------------------------------------------------
# SMS CONFIGURATION (TWILIO)
# -----------------------------------------------------------------------------
# Get from: https://console.twilio.com/
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_FROM_PHONE=+1234567890

# WhatsApp (Optional - requires approval)
# TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# -----------------------------------------------------------------------------
# MONITORING & OBSERVABILITY
# -----------------------------------------------------------------------------
# Sentry - Get from: https://sentry.io/
SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=0.1

# Logging
LOG_FORMAT=json
LOG_FILE=logs/app.log

# -----------------------------------------------------------------------------
# CORS & SECURITY
# -----------------------------------------------------------------------------
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
ALLOWED_HOSTS=localhost,127.0.0.1

# Rate Limiting (requests per minute)
RATE_LIMIT_LOGIN=5
RATE_LIMIT_API=60
RATE_LIMIT_WEBHOOK=100

# -----------------------------------------------------------------------------
# FEATURE FLAGS
# -----------------------------------------------------------------------------
ENABLE_RAZORPAY=false
ENABLE_PAYU=false
ENABLE_CASHFREE=false
ENABLE_WHATSAPP=false
ENABLE_ANALYTICS_EXPORT=true

# -----------------------------------------------------------------------------
# ANALYTICS & DATA (OPTIONAL)
# -----------------------------------------------------------------------------
# ClickHouse (for high-volume analytics)
# CLICKHOUSE_URL=http://localhost:8123
# CLICKHOUSE_USER=default
# CLICKHOUSE_PASSWORD=

# S3 (for data exports)
# S3_BUCKET=tinko-recovery-exports
# S3_ACCESS_KEY=your_access_key
# S3_SECRET_KEY=your_secret_key
# S3_REGION=us-east-1

# -----------------------------------------------------------------------------
# WEBHOOK CONFIGURATION
# -----------------------------------------------------------------------------
WEBHOOK_TIMEOUT=30
WEBHOOK_RETRY_MAX=3
WEBHOOK_RETRY_DELAY=60

# -----------------------------------------------------------------------------
# RECOVERY LINK SETTINGS
# -----------------------------------------------------------------------------
RECOVERY_LINK_EXPIRY_DAYS=7
RECOVERY_LINK_BASE_URL=http://localhost:3000/pay/retry

# -----------------------------------------------------------------------------
# NOTIFICATION SETTINGS
# -----------------------------------------------------------------------------
NOTIFICATION_RETRY_MAX=3
NOTIFICATION_RETRY_DELAY=300

# -----------------------------------------------------------------------------
# END OF CONFIGURATION
# -----------------------------------------------------------------------------
```

---

### Frontend `.env.local` File

Create this file: `tinko-console/.env.local`

```env
# =============================================================================
# TINKO RECOVERY PLATFORM - FRONTEND CONFIGURATION
# =============================================================================
# Generated: October 21, 2025
# Environment: development
# =============================================================================

# -----------------------------------------------------------------------------
# API CONFIGURATION
# -----------------------------------------------------------------------------
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# -----------------------------------------------------------------------------
# NEXTAUTH CONFIGURATION
# -----------------------------------------------------------------------------
# Generate with: openssl rand -base64 32
NEXTAUTH_SECRET=CHANGE_THIS_TO_RANDOM_32_CHAR_STRING
NEXTAUTH_URL=http://localhost:3000

# -----------------------------------------------------------------------------
# STRIPE (CLIENT-SIDE)
# -----------------------------------------------------------------------------
# Get from: https://dashboard.stripe.com/apikeys
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_51xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# -----------------------------------------------------------------------------
# RAZORPAY (CLIENT-SIDE)
# -----------------------------------------------------------------------------
# Get from: https://dashboard.razorpay.com/app/keys
NEXT_PUBLIC_RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxxxxx

# -----------------------------------------------------------------------------
# SENTRY (CLIENT-SIDE)
# -----------------------------------------------------------------------------
# Get from: https://sentry.io/
NEXT_PUBLIC_SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
NEXT_PUBLIC_SENTRY_ENVIRONMENT=development

# -----------------------------------------------------------------------------
# FEATURE FLAGS
# -----------------------------------------------------------------------------
NEXT_PUBLIC_ENABLE_RAZORPAY=false
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_NOTIFICATIONS=true
NEXT_PUBLIC_ENABLE_DARK_MODE=true

# -----------------------------------------------------------------------------
# ANALYTICS (OPTIONAL)
# -----------------------------------------------------------------------------
# Google Analytics
# NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX

# Mixpanel
# NEXT_PUBLIC_MIXPANEL_TOKEN=your_token_here

# -----------------------------------------------------------------------------
# END OF CONFIGURATION
# -----------------------------------------------------------------------------
```

---

## ✅ VERIFICATION CHECKLIST

### Step 1: Core Services

```bash
# Check Python version
python --version  # Should be 3.9+

# Check Node version
node --version  # Should be 18+

# Check Docker
docker --version  # Should be installed

# Check Redis
docker ps | grep tinko-redis  # Should be running
```

---

### Step 2: Backend Setup

```bash
cd Stealth-Reecovery

# Install dependencies
pip install -r requirements.txt

# Check database connection
python -c "from app.db import engine; print('DB Connected!' if engine else 'Failed')"

# Run migrations
alembic upgrade head

# Test backend server
python -m uvicorn app.main:app --reload
# Should start on http://localhost:8000

# In another terminal, test health check
curl http://localhost:8000/healthz
# Should return: {"status":"healthy"}
```

---

### Step 3: Frontend Setup

```bash
cd tinko-console

# Install dependencies
npm install

# Build frontend
npm run build

# Start development server
npm run dev
# Should start on http://localhost:3000

# Test frontend
curl http://localhost:3000
# Should return HTML
```

---

### Step 4: Test Integrations

```bash
cd Stealth-Reecovery

# Test Stripe
curl -X POST http://localhost:8000/v1/payments/stripe/checkout-sessions \
  -H "Content-Type: application/json" \
  -d '{"amount": 5000, "currency": "usd", "transaction_ref": "TEST123"}'

# Test Email
python -c "
from app.services.email_service import email_service
result = email_service.send_email('test@example.com', 'Test', '<h1>Hi</h1>')
print('Email works!' if result else 'Email failed!')
"

# Test SMS (if configured)
python -c "
from app.services.sms_service import sms_service
result = sms_service.send_sms('+1234567890', 'Test SMS')
print('SMS works!' if result else 'SMS failed!')
"

# Run test suite
pytest -v
# Should pass 48/55 tests (87.3%)
```

---

### Step 5: Celery Workers

```bash
cd Stealth-Reecovery

# Start Celery worker
celery -A app.worker worker --loglevel=info --pool=solo
# Should connect to Redis and show available tasks

# In another terminal, start Celery beat
celery -A app.worker beat --loglevel=info
# Should show scheduled tasks

# Test retry task
python -c "
from app.tasks.retry_tasks import trigger_immediate_retry
result = trigger_immediate_retry.delay(1)
print(f'Task ID: {result.id}')
print('Check Celery worker logs!')
"
```

---

## 🚨 COMMON ISSUES & SOLUTIONS

### Issue 1: Database Connection Failed

**Error:** `Could not connect to database`

**Solutions:**

```bash
# For SQLite: Check file permissions
ls -la recovery.db

# For PostgreSQL: Test connection
psql -h localhost -U tinko -d tinko_recovery -c "SELECT 1;"

# Check DATABASE_URL format
echo $DATABASE_URL
```

---

### Issue 2: Redis Connection Failed

**Error:** `Error connecting to Redis`

**Solutions:**

```bash
# Check if Redis is running
docker ps | grep redis

# Start Redis if not running
docker start tinko-redis

# Test Redis connection
docker exec tinko-redis redis-cli ping

# Check REDIS_URL
echo $REDIS_URL
```

---

### Issue 3: Stripe Webhook Signature Verification Failed

**Error:** `Invalid webhook signature`

**Solutions:**

```bash
# Use Stripe CLI for local testing
stripe listen --forward-to localhost:8000/v1/webhooks/stripe

# Copy the webhook signing secret shown
# Update STRIPE_WEBHOOK_SECRET in .env

# Test webhook
stripe trigger payment_intent.succeeded
```

---

### Issue 4: Email Not Sending

**Error:** `SMTP authentication failed`

**Solutions:**

```bash
# For Gmail:
# 1. Enable 2FA: https://myaccount.google.com/security
# 2. Generate App Password: https://myaccount.google.com/apppasswords
# 3. Use 16-char password (remove spaces)

# Test SMTP connection
python -c "
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your.email@gmail.com', 'your_app_password')
print('SMTP works!')
server.quit()
"
```

---

### Issue 5: Celery Tasks Not Running

**Error:** `Task never completes`

**Solutions:**

```bash
# Check worker is running
ps aux | grep celery

# Check worker logs
celery -A app.worker worker --loglevel=debug

# Check task is registered
celery -A app.worker inspect registered

# Restart worker with
celery -A app.worker worker --loglevel=info --pool=solo
```

---

## 🎯 QUICK START COMMANDS

### Complete Setup in One Go

```bash
#!/bin/bash
# Save this as: setup_tinko.sh

echo "🚀 Setting up Tinko Recovery Platform..."

# 1. Start Redis
docker run -d --name tinko-redis -p 6379:6379 redis:alpine
echo "✅ Redis started"

# 2. Setup backend
cd Stealth-Reecovery
pip install -r requirements.txt
alembic upgrade head
echo "✅ Backend ready"

# 3. Setup frontend
cd tinko-console
npm install
echo "✅ Frontend ready"

# 4. Seed demo data
cd ..
python scripts/seed_demo_data.py
echo "✅ Demo data loaded"

echo "
🎉 Setup Complete!

Start services:
1. Backend:  cd Stealth-Reecovery && uvicorn app.main:app --reload
2. Frontend: cd tinko-console && npm run dev
3. Worker:   celery -A app.worker worker --loglevel=info --pool=solo
4. Beat:     celery -A app.worker beat --loglevel=info

Access:
- Backend:   http://localhost:8000
- Frontend:  http://localhost:3000
- API Docs:  http://localhost:8000/docs
- Dashboard: http://localhost:3000/dashboard

Login:
- Email:    demo@example.com
- Password: demo123
"
```

---

## 📚 ADDITIONAL RESOURCES

### Documentation Links

- **Stripe Docs:** https://stripe.com/docs/api
- **Razorpay Docs:** https://razorpay.com/docs/
- **Twilio Docs:** https://www.twilio.com/docs/
- **Celery Docs:** https://docs.celeryproject.org/
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Next.js Docs:** https://nextjs.org/docs

### Support

- **GitHub Issues:** https://github.com/stealthorga-crypto/STEALTH-TINKO/issues
- **Email:** support@tinko.in

---

## 🎓 SUMMARY

### Minimum Required (Free - 30 minutes)

1. ✅ Database: SQLite (automatic)
2. ✅ Redis: Docker (free)
3. ✅ Stripe: Test mode (free)
4. ✅ Gmail: SMTP (free, 500/day)
5. ✅ JWT: Generated secret (free)

### Recommended for Production (2 hours)

1. ✅ Database: Supabase PostgreSQL (free tier)
2. ✅ Redis: Upstash (free tier)
3. ✅ Stripe: Live mode (2.9% + $0.30)
4. ✅ SendGrid: Email (free 100/day)
5. ✅ Twilio: SMS ($15 trial)
6. ✅ Sentry: Error tracking (free 5k events)
7. ✅ Razorpay: Indian payments (2%)

### Total Cost Estimate

- **Development:** $0/month (all free tiers)
- **Production (small):** ~$20-30/month
- **Production (medium):** ~$100-200/month
- **Enterprise:** Custom pricing

---

**🎉 You're Ready to Launch!**

Save this guide and follow each section step-by-step. All the credentials and keys are clearly documented with examples and test commands.

---

_Last Updated: October 21, 2025_  
_For: Tinko Recovery Platform v1.0_  
_Repository: stealthorga-crypto/STEALTH-TINKO_
