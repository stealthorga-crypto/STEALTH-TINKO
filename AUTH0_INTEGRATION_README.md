# 🔐 Auth0 Passwordless OTP Integration

Complete Auth0 integration with Passwordless OTP (Email/SMS), Email+Password, and Google OAuth for the Tinko Recovery Platform.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Auth0 Setup](#auth0-setup)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Architecture](#architecture)
- [Security](#security)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This integration provides:

1. **Passwordless OTP Authentication** (SMS or Email)
2. **Email + Password Authentication** (Database connection)
3. **Google OAuth** (Social login)
4. **JWT-based API Protection** (RS256 tokens)
5. **Rate Limiting** (Redis-backed or in-memory)
6. **Session Management** (HttpOnly secure cookies)

**Authentication Flow:**

```
User Signup → Auth0 User Created → OTP Sent → OTP Verified →
Session Created → Dashboard Access → Protected API Calls
```

---

## ✨ Features

- ✅ **Passwordless OTP** via Email or SMS (Twilio)
- ✅ **Database Connection** for Email+Password
- ✅ **Google Social Login**
- ✅ **RS256 JWT Verification** in FastAPI
- ✅ **Rate Limiting** on OTP endpoints
- ✅ **Secure HttpOnly Cookies** for sessions
- ✅ **SSR Session Guards** in Next.js
- ✅ **User Metadata** (company, phone) storage
- ✅ **Auth0 Actions** for post-login processing
- ✅ **Production-ready** error handling

---

## 📦 Prerequisites

### Required Accounts

1. **Auth0 Account** (Free tier works)

   - Sign up at: https://auth0.com/signup
   - Note your **Domain**, **Client ID**, and **Client Secret**

2. **Twilio Account** (Optional, for SMS OTP)

   - Sign up at: https://www.twilio.com/try-twilio
   - Get your **Account SID** and **Auth Token**
   - Get a **Phone Number**

3. **Google Cloud Console** (Optional, for Google OAuth)
   - Create OAuth 2.0 credentials
   - Note your **Client ID** and **Client Secret**

### Required Software

- Node.js 18+ and npm
- Python 3.10+
- Redis (optional, for production rate limiting)

---

## 🔧 Auth0 Setup

### Step 1: Create Auth0 Application

1. Go to **Auth0 Dashboard** → **Applications** → **Create Application**
2. Choose **Regular Web Application**
3. Note your **Domain**, **Client ID**, and **Client Secret**

4. **Configure Application Settings:**

   ```
   Allowed Callback URLs:
   http://localhost:3000/api/auth/callback, http://localhost:3000/auth0/callback

   Allowed Logout URLs:
   http://localhost:3000, http://localhost:3000/auth0/signin

   Allowed Web Origins:
   http://localhost:3000
   ```

### Step 2: Enable Passwordless Connections

#### For Email OTP:

1. Go to **Authentication** → **Passwordless**
2. Click **Email**
3. **Enable** the connection
4. **Configure Email Provider:**
   - **Built-in Email** (for testing)
   - **Custom SMTP** (for production - recommended: SendGrid, Mailgun)
5. **OTP Settings:**

   - ✅ Send a verification code (6-digit)
   - Code expires in: 300 seconds (5 minutes)

6. **Enable for your Application:**
   - Go to **Applications** tab
   - Enable for your app

#### For SMS OTP (Twilio):

1. Go to **Authentication** → **Passwordless**
2. Click **SMS**
3. **Enable** the connection

4. **Configure Twilio:**

   ```
   Twilio Account SID: <your_account_sid>
   Auth Token: <your_auth_token>
   From Phone Number: <your_twilio_number>
   ```

5. **SMS Message Template:**

   ```
   Your Tinko verification code is: @@password@@
   Valid for 5 minutes.
   ```

6. **Enable for your Application:**
   - Go to **Applications** tab
   - Enable for your app

### Step 3: Enable Database Connection

1. Go to **Authentication** → **Database**
2. Click **Username-Password-Authentication** (or create new)
3. **Enable** for your application
4. **Configure:**
   ```
   ✅ Requires Username: No
   ✅ Requires Email Verification: No (we handle via OTP)
   Password Policy: Good (or customize)
   ```

### Step 4: Enable Google OAuth (Optional)

1. **Create Google OAuth Credentials:**

   - Go to https://console.cloud.google.com
   - Create OAuth 2.0 Client ID
   - Authorized redirect URI: `https://dev-2cel36lijmqgl653.us.auth0.com/login/callback`

2. **Configure in Auth0:**
   - Go to **Authentication** → **Social**
   - Click **Google**
   - Enter your Google **Client ID** and **Client Secret**
   - Enable for your application

### Step 5: Create Auth0 API (Optional, for Audience)

1. Go to **Applications** → **APIs** → **Create API**
2. **Identifier**: `https://api.tinko.app` (or your domain)
3. **Signing Algorithm**: RS256
4. Enable for your application

### Step 6: Deploy Auth0 Action

1. Go to **Actions** → **Flows** → **Login**
2. Click **Custom** → **Build Custom**
3. Name: `Mark Passwordless Verified`
4. Paste code from `auth0/actions/post-login-mark-verified.js`
5. **Deploy**
6. Add to your **Login Flow** (drag and drop)

### Step 7: Rotate Client Secret

⚠️ **IMPORTANT: Never commit your client secret to Git!**

1. Go to **Applications** → Your App → **Settings**
2. Click **Rotate Secret**
3. Copy the new secret immediately
4. Update your `.env` files

---

## 📥 Installation

### Frontend (Next.js)

```bash
cd tinko-console

# Install dependencies
npm install

# Add new Auth0 dependencies
npm install jose zod ioredis
```

### Backend (FastAPI)

```bash
# Install Auth0-compatible dependencies
pip install -r requirements.auth0.txt

# Or install individually
pip install python-jose[cryptography] cryptography requests
```

---

## ⚙️ Configuration

### Frontend Environment Variables

Create or update `tinko-console/.env.local`:

```env
# Auth0 Configuration
AUTH0_DOMAIN=dev-2cel36lijmqgl653.us.auth0.com
AUTH0_CLIENT_ID=EyKSjReosjGlhiy1ln532x1ExbM1Ulzo
AUTH0_CLIENT_SECRET=<YOUR_ROTATED_CLIENT_SECRET>
AUTH0_ISSUER_BASE_URL=https://dev-2cel36lijmqgl653.us.auth0.com
AUTH0_BASE_URL=http://localhost:3000
AUTH0_AUDIENCE=https://api.tinko.app  # Optional

# OTP Channel: sms or email
OTP_CHANNEL=email

# Session Secret (generate with: openssl rand -hex 32)
SESSION_SECRET=<GENERATE_RANDOM_HEX_64_CHARS>
SESSION_COOKIE_NAME=auth_session
SESSION_MAX_AGE=86400

# Redis (optional, for rate limiting)
REDIS_URL=redis://localhost:6379/0

# API Configuration
NEXT_PUBLIC_API_URL=http://127.0.0.1:8010
BACKEND_URL=http://127.0.0.1:8010

# Rate Limiting
RATE_LIMIT_OTP_SEND=5
RATE_LIMIT_OTP_VERIFY=10

# Environment
NODE_ENV=development
```

**Generate SESSION_SECRET:**

```bash
# On Linux/Mac:
openssl rand -hex 32

# On Windows (PowerShell):
-join ((1..32) | ForEach-Object { '{0:X2}' -f (Get-Random -Max 256) })
```

### Backend Environment Variables

Create or update `.env.auth0.backend`:

```env
# Auth0 Configuration
AUTH0_DOMAIN=dev-2cel36lijmqgl653.us.auth0.com
AUTH0_ISSUER=https://dev-2cel36lijmqgl653.us.auth0.com/
AUTH0_AUDIENCE=https://api.tinko.app  # Optional, but recommended

# API Configuration
API_HOST=0.0.0.0
API_PORT=8010

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

---

## 🚀 Running the Application

### Development Mode

#### Start Backend (FastAPI):

```bash
# Using the Auth0-enabled main file
uvicorn app.main_auth0:app --host 127.0.0.1 --port 8010 --reload
```

#### Start Frontend (Next.js):

```bash
cd tinko-console
npm run dev
```

#### Start Redis (Optional, for rate limiting):

```bash
# Docker
docker run -d --name redis -p 6379:6379 redis:alpine

# Or use local Redis
redis-server
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://127.0.0.1:8010/docs
- **Auth0 Signup**: http://localhost:3000/auth0/signup
- **Auth0 Dashboard**: http://localhost:3000/auth0/dashboard

---

## 🧪 Testing

### Test Signup Flow

1. Go to http://localhost:3000/auth0/signup
2. Fill in:
   - Company: Test Company
   - Email: test@example.com
   - Phone: +12345678901
   - Password: TestPass123!
3. Click "Create Account & Send OTP"
4. Check your email/SMS for the 6-digit OTP
5. Enter OTP on verification page
6. You'll be redirected to the dashboard

### Test Protected API

```bash
# Get a token from the session after login
# Then call the protected endpoint:

curl -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
     http://127.0.0.1:8010/private

# Expected response:
{
  "message": "This is a protected route",
  "user": {
    "sub": "auth0|...",
    "email": "test@example.com",
    ...
  }
}
```

### Test Google OAuth

1. Go to http://localhost:3000/auth0/signin
2. Click "Sign in with Google"
3. Complete Google authentication
4. You'll be redirected to the dashboard

---

## 🏗️ Architecture

### Authentication Flow

```
┌─────────────┐
│  Frontend   │
│  (Next.js)  │
└──────┬──────┘
       │
       │ 1. Signup (company, email, phone, password)
       ↓
┌─────────────┐
│   Auth0     │
│ DB Connection│
└──────┬──────┘
       │
       │ 2. User created with user_metadata
       ↓
┌─────────────┐
│   Auth0     │
│ Passwordless│
└──────┬──────┘
       │
       │ 3. Send OTP (SMS/Email)
       ↓
┌─────────────┐
│    User     │
│ Receives OTP│
└──────┬──────┘
       │
       │ 4. Submit OTP
       ↓
┌─────────────┐
│   Auth0     │
│ Verify OTP  │
└──────┬──────┘
       │
       │ 5. Return JWT tokens (access_token, id_token)
       ↓
┌─────────────┐
│  Frontend   │
│ Create Session│
└──────┬──────┘
       │
       │ 6. Set HttpOnly cookie
       ↓
┌─────────────┐
│  Dashboard  │
│  (Protected)│
└──────┬──────┘
       │
       │ 7. API calls with Bearer token
       ↓
┌─────────────┐
│  FastAPI    │
│ Verify RS256│
│   JWT       │
└─────────────┘
```

### Security Layers

1. **Auth0 Authentication** - Industry-standard OAuth 2.0
2. **RS256 JWT Signatures** - Asymmetric cryptography
3. **HttpOnly Cookies** - XSS protection
4. **Rate Limiting** - Brute-force protection
5. **HTTPS Only** (production) - Man-in-the-middle protection
6. **Secure SameSite** - CSRF protection

---

## 🔒 Security

### Best Practices Implemented

✅ **Never hardcode secrets** - All sensitive data in environment variables
✅ **Client secret not in browser** - Server-side API routes only
✅ **HttpOnly cookies** - JavaScript cannot access session tokens
✅ **Secure flag** (production) - Cookies only over HTTPS
✅ **SameSite=lax** - CSRF protection
✅ **Rate limiting** - Prevent brute-force attacks
✅ **Token expiration** - Short-lived access tokens
✅ **JWKS key rotation** - Automatic public key updates

### Environment-Specific Configuration

**Development:**

- `NODE_ENV=development`
- `Secure=false` (allows HTTP)
- Detailed error messages

**Production:**

- `NODE_ENV=production`
- `Secure=true` (requires HTTPS)
- Generic error messages
- Enable Redis for rate limiting

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "Invalid token: key not found"

**Cause:** JWKS cache issue or wrong Auth0 domain

**Fix:**

```bash
# Verify your AUTH0_DOMAIN matches exactly
# It should be: dev-2cel36lijmqgl653.us.auth0.com
# NOT: https://dev-2cel36lijmqgl653.us.auth0.com (no https://)

# Check JWKS URL is accessible:
curl https://dev-2cel36lijmqgl653.us.auth0.com/.well-known/jwks.json
```

#### 2. "Too many requests"

**Cause:** Hit rate limit

**Fix:**

- Wait for the cooldown period (shown in error)
- Adjust rate limits in `.env`:
  ```env
  RATE_LIMIT_OTP_SEND=10  # Increase if needed
  RATE_LIMIT_OTP_VERIFY=20
  ```

#### 3. "Failed to send OTP"

**Cause:** Passwordless connection not enabled or misconfigured

**Fix:**

1. Go to Auth0 Dashboard → Authentication → Passwordless
2. Ensure Email or SMS is **enabled**
3. Check it's enabled for your **Application**
4. For SMS: Verify Twilio credentials
5. For Email: Test email provider

#### 4. "Unauthorized" on protected routes

**Cause:** Token not sent or invalid

**Fix:**

```bash
# Check token is being sent:
curl -v -H "Authorization: Bearer <token>" http://127.0.0.1:8010/private

# Verify token at: https://jwt.io
# Check:
# - iss (issuer) matches AUTH0_ISSUER
# - aud (audience) matches AUTH0_AUDIENCE (if set)
# - exp (expiration) is in the future
```

#### 5. Session not persisting

**Cause:** Cookie not being set or read

**Fix:**

1. Check `SESSION_SECRET` is set
2. Verify domain matches (localhost vs 127.0.0.1)
3. In production, ensure `Secure=true` and using HTTPS
4. Check browser console for cookie errors

### Debug Mode

Enable detailed logging:

**Frontend:**

```typescript
// In lib/auth0.ts, add console.logs
console.log("Auth0 Config:", { domain, clientId });
```

**Backend:**

```python
# In app/auth0_auth.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📚 Additional Resources

- **Auth0 Docs**: https://auth0.com/docs
- **Passwordless**: https://auth0.com/docs/authenticate/passwordless
- **JWT Debugger**: https://jwt.io
- **Next.js Auth**: https://nextjs.org/docs/authentication
- **FastAPI Security**: https://fastapi.tiangolo.com/tutorial/security/

---

## 📝 Notes

### Switching from Email to SMS OTP

Update `.env.local`:

```env
OTP_CHANNEL=sms  # Change from 'email' to 'sms'
```

Ensure SMS Passwordless is enabled in Auth0 Dashboard.

### Using Custom Email Provider

1. Go to Auth0 Dashboard → Authentication → Passwordless → Email
2. Choose "Use my own Email Provider"
3. Configure SMTP settings (recommended: SendGrid, Mailgun)

### Adding More Scopes

1. Define in Auth0 API permissions
2. Request in token:
   ```typescript
   scope: "openid profile email admin:access";
   ```
3. Check in backend:
   ```python
   @app.get("/admin")
   async def admin(user = Depends(require_scope("admin:access"))):
       ...
   ```

---

## ✅ Checklist

Before going to production:

- [ ] Rotate Auth0 client secret
- [ ] Enable HTTPS (Let's Encrypt)
- [ ] Set `NODE_ENV=production`
- [ ] Enable Redis for rate limiting
- [ ] Configure custom email provider (not built-in)
- [ ] Set up monitoring (Sentry, DataDog)
- [ ] Review CORS origins
- [ ] Test all authentication flows
- [ ] Enable MFA (optional)
- [ ] Review Auth0 Rules/Actions
- [ ] Set appropriate token expiration
- [ ] Configure proper error pages

---

**Need Help?** Check the terminal logs for detailed error messages!
