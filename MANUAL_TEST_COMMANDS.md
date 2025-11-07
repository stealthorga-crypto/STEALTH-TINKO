# Auth0 Passwordless OTP - Manual Test Commands

## Prerequisites

1. Backend running: `http://127.0.0.1:8010`
2. Auth0 credentials configured in `.env`
3. Real Gmail account to receive OTP

---

## Test 1: Send OTP (Register Start)

### Command:

```bash
curl -i -X POST http://127.0.0.1:8010/v1/auth/register/start \
  -H "Content-Type: application/json" \
  -d '{
    "email": "YOUR_TEST_EMAIL@gmail.com",
    "password": "TestPass123!",
    "full_name": "Test User",
    "org_name": "Test Org"
  }'
```

### Expected Response:

```
HTTP/1.1 200 OK
Content-Type: application/json

{"ok":true,"message":"OTP sent to email"}
```

### Verification Checklist:

- [ ] HTTP status code is 200
- [ ] Response contains `"ok": true`
- [ ] Response does NOT contain any 6-digit code
- [ ] Terminal logs do NOT show OTP code
- [ ] Gmail inbox receives email from Auth0 with 6-digit code

### What to Do Next:

1. Check your Gmail inbox (including spam folder)
2. Find email from Auth0
3. Copy the 6-digit verification code
4. Proceed to Test 2

---

## Test 2: Verify OTP (Register Verify)

### Command:

Replace `YOUR_OTP_CODE` with the 6-digit code from Gmail.

```bash
curl -i -X POST http://127.0.0.1:8010/v1/auth/register/verify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "YOUR_TEST_EMAIL@gmail.com",
    "password": "TestPass123!",
    "full_name": "Test User",
    "org_name": "Test Org",
    "code": "YOUR_OTP_CODE"
  }'
```

### Example with actual OTP:

```bash
curl -i -X POST http://127.0.0.1:8010/v1/auth/register/verify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@gmail.com",
    "password": "TestPass123!",
    "full_name": "Test User",
    "org_name": "Test Org",
    "code": "123456"
  }'
```

### Expected Response (Success):

```
HTTP/1.1 200 OK
Content-Type: application/json

{"ok":true,"message":"Email verified. You can now sign in."}
```

### Expected Response (Invalid/Expired OTP):

```
HTTP/1.1 400 Bad Request
Content-Type: application/json

{"detail":"Invalid or expired verification code"}
```

### Verification Checklist:

- [ ] HTTP status code is 200 (on success)
- [ ] Response contains `"ok": true`
- [ ] Response does NOT contain the OTP code you entered
- [ ] Terminal logs do NOT show the OTP code
- [ ] User is created in Neon Postgres database

### Database Verification:

```sql
-- Connect to your Neon Postgres database and run:
SELECT id, email, full_name, is_active, created_at
FROM users
WHERE email = 'YOUR_TEST_EMAIL@gmail.com';
```

Expected result:

- User exists with `is_active = true`
- Email matches test email
- `created_at` is recent timestamp

---

## Test 3: Login with Email + Password

### Command:

```bash
curl -i -X POST http://127.0.0.1:8010/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "YOUR_TEST_EMAIL@gmail.com",
    "password": "TestPass123!"
  }'
```

### Expected Response (Success):

```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "YOUR_TEST_EMAIL@gmail.com",
    "full_name": "Test User",
    "role": "admin",
    "is_active": true,
    "org_id": 1,
    "created_at": "2025-11-07T16:00:00.000Z"
  },
  "organization": {
    "id": 1,
    "name": "Test Org",
    "slug": "test-org",
    "is_active": true,
    "created_at": "2025-11-07T16:00:00.000Z"
  }
}
```

### Expected Response (Invalid Credentials):

```
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{"detail":"Incorrect email or password"}
```

### Verification Checklist:

- [ ] HTTP status code is 200
- [ ] Response contains `access_token`
- [ ] Token is a valid JWT (3 parts separated by dots)
- [ ] User object contains correct email
- [ ] Organization object is present

### JWT Token Verification:

Copy the `access_token` value and decode it at https://jwt.io

Expected claims:

```json
{
  "user_id": 1,
  "org_id": 1,
  "role": "admin",
  "exp": <future_timestamp>,
  "iat": <current_timestamp>
}
```

---

## Test 4: Access Protected Endpoint with JWT

### Command:

Replace `YOUR_JWT_TOKEN` with the `access_token` from Test 3.

```bash
curl -i http://127.0.0.1:8010/v1/auth/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Expected Response:

```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 1,
  "email": "YOUR_TEST_EMAIL@gmail.com",
  "full_name": "Test User",
  "role": "admin",
  "is_active": true,
  "org_id": 1,
  "created_at": "2025-11-07T16:00:00.000Z"
}
```

---

## Security Verification Tests

### Test 5: Verify NO OTP in Terminal Logs

1. Keep terminal window visible where backend is running
2. Run Test 1 (Send OTP)
3. Check terminal output

**Expected:**

- You should see: `INFO: ... "POST /v1/auth/register/start HTTP/1.1" 200 OK`
- You should see structured logs like: `{"event": "auth0_otp_triggered", "email": "..."}`
- You should **NOT** see any 6-digit codes
- You should **NOT** see log lines like "OTP CODE: 123456"

### Test 6: Verify Email Already Registered

Try registering the same email twice:

```bash
# First attempt - should succeed (if email is new)
curl -X POST http://127.0.0.1:8010/v1/auth/register/start \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Pass123!","full_name":"Test","org_name":"Org"}'

# After verifying above, try again - should fail
curl -i -X POST http://127.0.0.1:8010/v1/auth/register/start \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Pass123!","full_name":"Test","org_name":"Org"}'
```

**Expected:**

```
HTTP/1.1 400 Bad Request
{"detail":"Email already registered"}
```

---

## Troubleshooting

### Issue: "Failed to send verification email"

**Cause:** Auth0 configuration issue

**Solution:**

1. Check `.env` file has correct Auth0 credentials
2. Verify `AUTH0_CLIENT_ID` and `AUTH0_CLIENT_SECRET` are correct
3. Ensure Auth0 Passwordless Email connection is enabled in Auth0 dashboard

### Issue: "Invalid or expired verification code"

**Causes:**

1. OTP expired (usually valid for ~5-10 minutes)
2. Wrong OTP code entered
3. OTP already used

**Solution:**

1. Request new OTP (run Test 1 again)
2. Check Gmail for latest email
3. Copy code carefully

### Issue: "Email already registered"

**Cause:** User already exists in database

**Solution:**

- Use different email, OR
- Delete existing user from database, OR
- Proceed to Test 3 (login) directly

---

## Complete Flow Example

Here's a complete example with real values (replace with your actual email):

```bash
# 1. Send OTP
curl -X POST http://127.0.0.1:8010/v1/auth/register/start \
  -H "Content-Type: application/json" \
  -d '{
    "email": "srinath8789@gmail.com",
    "password": "MySecurePass123!",
    "full_name": "Srinath Kumar",
    "org_name": "Blocks and Loops"
  }'

# Response: {"ok":true,"message":"OTP sent to email"}
# → Check Gmail for OTP (e.g., 456789)

# 2. Verify OTP
curl -X POST http://127.0.0.1:8010/v1/auth/register/verify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "srinath8789@gmail.com",
    "password": "MySecurePass123!",
    "full_name": "Srinath Kumar",
    "org_name": "Blocks and Loops",
    "code": "456789"
  }'

# Response: {"ok":true,"message":"Email verified. You can now sign in."}

# 3. Login
curl -X POST http://127.0.0.1:8010/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "srinath8789@gmail.com",
    "password": "MySecurePass123!"
  }'

# Response: {"access_token":"eyJhbG...","token_type":"bearer","user":{...},"organization":{...}}
```

---

## Automated Testing

Run the integration tests:

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run Auth0 flow tests
pytest tests/test_auth0_flow.py -v

# Run with coverage
pytest tests/test_auth0_flow.py --cov=app/routers/auth --cov=app/services/auth0_otp_service -v
```

Expected output:

```
tests/test_auth0_flow.py::TestAuth0PasswordlessFlow::test_register_start_calls_auth0 PASSED
tests/test_auth0_flow.py::TestAuth0PasswordlessFlow::test_register_verify_creates_user_on_valid_otp PASSED
tests/test_auth0_flow.py::TestAuth0PasswordlessFlow::test_login_returns_jwt_for_valid_user PASSED
tests/test_auth0_flow.py::TestSecurityGuarantees::test_otp_never_in_exception_messages PASSED

============== 4 passed in 2.34s ==============
```

---

## Success Criteria

✅ All tests pass  
✅ OTP is received in Gmail inbox  
✅ OTP is NEVER visible in terminal logs  
✅ OTP is NEVER returned in API responses  
✅ User is created in database after verification  
✅ Login returns valid JWT token  
✅ JWT token works for protected endpoints

**If all criteria are met, the Auth0 Passwordless OTP flow is working correctly!** 🎉
