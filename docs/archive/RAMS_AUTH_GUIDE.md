# Ram's Authentication Guide 🔐

Welcome Ram! This guide shows you all the ways to sign up and sign in to the Tinko Recovery platform, plus how to use your API keys for integration.

## 🎯 Quick Start Options

You have **multiple ways** to get started, and they all work with the **same email address**:

### Option 1: Traditional Sign-up
- Sign up with email/password
- Get API keys automatically (for customers)
- Can later sign in with password OR OTP

### Option 2: Google Sign-up  
- Sign up with your Google account
- Provide business details during flow
- Get API keys automatically (for customers)
- Can later sign in with Google OR OTP

## 📋 Complete Authentication Flows

### 1. Email/Password Registration

**For Ram as a customer with API integration needs:**

```bash
curl -X POST http://localhost:8010/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ram@rams-business.com",
    "password": "SecurePassword123!",
    "full_name": "Ram Kumar",
    "org_name": "Ram'\''s Business Solutions",
    "org_slug": "rams-business",
    "account_type": "customer",
    "api_key_name": "Production API Key"
  }'
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "ram@rams-business.com",
    "full_name": "Ram Kumar",
    "account_type": "customer",
    "auth_providers": ["email"],
    "is_email_verified": false
  },
  "organization": {
    "id": 1,
    "name": "Ram's Business Solutions",
    "slug": "rams-business"
  }
}
```

### 2. Google OAuth Registration

**Step 1: Initiate Google registration with business details**

```bash
curl -X POST http://localhost:8010/v1/auth/register/google \
  -H "Content-Type: application/json" \
  -d '{
    "org_name": "Ram'\''s Tech Startup",
    "org_slug": "rams-tech",
    "account_type": "customer",
    "api_key_name": "Integration API Key"
  }'
```

**Step 2: Visit the redirect URL and authorize with Google**

The response will include a `redirect_url`. Visit it to complete Google OAuth.

## 🔑 Sign-in Methods (For Existing Users)

Once you're registered, you can sign in using **any of these methods**:

### Method 1: Email/Password Login

```bash
curl -X POST http://localhost:8010/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ram@rams-business.com",
    "password": "SecurePassword123!"
  }'
```

### Method 2: Email/OTP Login (Passwordless)

**Step 1: Request OTP**
```bash
curl -X POST http://localhost:8010/v1/auth/login/request-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "ram@rams-business.com"}'
```

**Step 2: Check your email and verify OTP**
```bash
curl -X POST http://localhost:8010/v1/auth/login/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ram@rams-business.com",
    "otp_code": "123456"
  }'
```

### Method 3: Google OAuth Login

Simply visit: `http://localhost:8010/v1/auth/oauth/google/start`

If your email is already registered, you'll be logged in automatically!

## 🔧 API Key Management

### List Your API Keys

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8010/v1/auth/api-keys
```

### Create New API Key

```bash
curl -X POST http://localhost:8010/v1/auth/api-keys \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "key_name": "Mobile App API",
    "scopes": ["read", "write"],
    "expires_in_days": 90
  }'
```

**⚠️ Important:** The API key is only shown once! Save it securely.

### Delete API Key

```bash
curl -X DELETE http://localhost:8010/v1/auth/api-keys/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🚀 Using API Keys for Integration

Once you have API keys, use them to access customer endpoints:

### Get Your Profile

```bash
curl -H "Authorization: Bearer sk_your_api_key_here" \
     http://localhost:8010/v1/customer/profile
```

### List Transactions

```bash
curl -H "X-API-Key: sk_your_api_key_here" \
     http://localhost:8010/v1/customer/transactions
```

### Create Transaction

```bash
curl -X POST \
  -H "Authorization: Bearer sk_your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_ref": "TXN-001", 
    "amount": 10000, 
    "currency": "USD",
    "customer_email": "customer@example.com"
  }' \
  http://localhost:8010/v1/customer/transactions
```

### Get Organization Stats

```bash
curl -H "Authorization: Bearer sk_your_api_key_here" \
     http://localhost:8010/v1/customer/organization/stats
```

## 🔒 Security Features

### OTP Security
- **10-minute expiry**: OTP codes expire after 10 minutes
- **3 attempts max**: Maximum 3 verification attempts per OTP
- **Single-use**: Each OTP can only be used once

### API Key Security
- **Scoped permissions**: Keys can have `read`, `write`, or `admin` scopes
- **Usage tracking**: Monitor key usage and last access times
- **Expiration**: Set custom expiration dates
- **Secure hashing**: Keys are hashed and never stored in plain text

### Authentication Flexibility
- **Multi-provider**: Use email/password, Google, or OTP with the same account
- **Unified identity**: All auth methods work with your email address
- **JWT tokens**: Secure session management
- **Customer account type**: Special features for business accounts

## 📊 Summary: Ram's Complete Journey

1. **Sign Up** (Choose one):
   - Email/Password + business details → Get API keys
   - Google OAuth + business details → Get API keys

2. **Sign In** (Any method):
   - Email/Password (traditional)
   - Email/OTP (passwordless)
   - Google OAuth (if linked)

3. **Integrate**:
   - Use API keys for programmatic access
   - Build applications using customer endpoints
   - Manage transactions and organization data

4. **Manage**:
   - Create/delete API keys as needed
   - Monitor usage and security
   - Scale your integration

## 🎉 Benefits for Ram

- **Multiple sign-up options**: Choose what works best for you
- **Passwordless option**: Sign in with just your email (OTP)
- **Google integration**: Quick sign-up/sign-in with Google account
- **Business features**: Organization management, API keys
- **Secure API access**: Scoped permissions, usage tracking
- **Unified account**: All auth methods work with same email

## 🛠️ Development Environment

For testing, check emails at: http://localhost:8025 (MailHog)

For production, configure SMTP settings in your `.env` file:
```env
SMTP_HOST=your-smtp-server.com
SMTP_PORT=587
SMTP_USER=your-smtp-username
SMTP_PASSWORD=your-smtp-password
SMTP_FROM=noreply@your-domain.com
SMTP_USE_TLS=true
```

---

**Questions?** Contact the development team or check the API documentation at `/docs` when the server is running.