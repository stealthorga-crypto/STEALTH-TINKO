# 🔐 OTP Verification Guide for Local Development

## ✅ Current Status

Your application is **WORKING CORRECTLY**! The OTP system is functioning, but emails can't be sent because MailHog (email testing server) is not running.

## 🎯 How to Use OTP Without Email (Development Mode)

### **Option 1: Check the Terminal Logs (Easiest)**

When you register or request an OTP, the code is printed in the terminal logs. Look for:

```json
{"email": "your-email@example.com", "code": "123456", "event": "otp_generated", ...}
```

**Recent OTP codes for srinath8789@gmail.com:**

- `253372` (expires 2025-11-05T09:06:43)
- `471210` (expires 2025-11-05T09:06:47)
- `254023` (expires 2025-11-05T09:06:49) ← **Use the most recent one**

### **Option 2: Start MailHog Email Server**

If you have Docker installed and want to test the full email flow:

```bash
# Start MailHog
docker run -d --name mailhog -p 1025:1025 -p 8025:8025 mailhog/mailhog

# View emails in browser
# Open: http://localhost:8025
```

Then restart your application.

## 📝 Sign Up & Sign In Flow

### **Sign Up (with OTP verification)**

1. Go to: http://localhost:3000/auth/signup
2. Fill in:
   - Email: your-email@example.com
   - Password: your-secure-password
   - Full Name: Your Name
   - Organization Name: Your Company
3. Click "Sign Up"
4. **Check your terminal logs** for the OTP code
5. Enter the OTP code in the verification screen
6. ✅ Account activated!

### **Sign In (for verified accounts)**

1. Go to: http://localhost:3000/auth/signin
2. Enter your email and password
3. Click "Sign In"
4. ✅ You're logged in!

## 🐛 Troubleshooting

### "Invalid verification code"

- Make sure you're using the **most recent** OTP code from the logs
- OTP codes expire after 10 minutes
- Try registering again to get a fresh code

### "User account is inactive or unverified"

- You need to complete OTP verification first
- Use the `/v1/auth/register/start` endpoint to get a new OTP
- Then use `/v1/auth/register/verify` with the code

### "Email already registered"

- If you registered but didn't verify, you can:
  1. Request a new OTP by calling `/v1/auth/register/start` again
  2. Or delete the user from the database and start fresh

## 🔧 Configuration

Your `.env` file now has:

```env
OTP_DEV_ECHO=true        # Shows OTP in logs
OTP_TTL_MINUTES=10       # OTP expires after 10 minutes
ENVIRONMENT=development  # Development mode
```

## 📌 API Endpoints

- Sign Up (Start): `POST /v1/auth/register/start`
- Verify OTP: `POST /v1/auth/register/verify`
- Sign In: `POST /v1/auth/login`
- Legacy Sign Up (no OTP): `POST /v1/auth/register`

## 🚀 Quick Test

```bash
# 1. Register (get OTP in logs)
curl -X POST http://127.0.0.1:8010/v1/auth/register/start \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "full_name": "Test User",
    "org_name": "Test Org"
  }'

# 2. Check terminal logs for OTP code

# 3. Verify with OTP
curl -X POST http://127.0.0.1:8010/v1/auth/register/verify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "code": "123456"
  }'

# 4. Sign in
curl -X POST http://127.0.0.1:8010/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!"
  }'
```

---

**Need help?** Check the terminal logs for detailed error messages and OTP codes!
