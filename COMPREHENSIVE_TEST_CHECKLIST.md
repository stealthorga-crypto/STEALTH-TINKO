# TINKO RECOVERY - COMPREHENSIVE FUNCTIONAL TEST CHECKLIST

**Test Date**: October 18, 2025  
**Tester**: ******\_\_\_******  
**Environment**: Local Development

---

## SETUP PREREQUISITES

### Backend Server

```bash
cd Stealth-Reecovery
C:/Python313/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Expected**: Server starts at http://127.0.0.1:8000

### Frontend Server

```bash
cd Stealth-Reecovery/tinko-console
npm run dev
```

**Expected**: Server starts at http://localhost:3000

---

## 1. BACKEND API ENDPOINTS

### 1.1 Health & Readiness

| Test            | Endpoint   | Method | Expected Status | Result |
| --------------- | ---------- | ------ | --------------- | ------ |
| Health check    | `/healthz` | GET    | 200             | ☐      |
| Readiness check | `/readyz`  | GET    | 200             | ☐      |

**Test Command**:

```bash
curl http://127.0.0.1:8000/healthz
curl http://127.0.0.1:8000/readyz
```

---

### 1.2 Event Ingestion (`/v1/events`)

#### Test Case: Create Payment Failed Event

| Step | Action                        | Expected Result              | Status |
| ---- | ----------------------------- | ---------------------------- | ------ |
| 1    | POST payment_failed event     | Status 201, returns event ID | ☐      |
| 2    | Verify transaction created    | Transaction exists in DB     | ☐      |
| 3    | GET events by transaction_ref | Returns list of events       | ☐      |

**Test Command**:

```bash
# Create event
curl -X POST http://127.0.0.1:8000/v1/events/payment_failed \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_ref": "TXN_TEST_001",
    "amount": 49999,
    "currency": "INR",
    "gateway": "stripe",
    "failure_reason": "insufficient_funds",
    "occurred_at": "2025-10-18T10:00:00Z",
    "metadata": {"customer_email": "test@example.com"}
  }'

# Get events
curl http://127.0.0.1:8000/v1/events/by_ref/TXN_TEST_001
```

**Expected Response**:

- Event ID returned
- Transaction created with amount, currency
- Failure event linked to transaction

---

### 1.3 Classifier (`/v1/classify`)

| Test Case          | Code                 | Message         | Expected Category | Status |
| ------------------ | -------------------- | --------------- | ----------------- | ------ |
| Insufficient funds | `insufficient_funds` | null            | `funds`           | ☐      |
| Auth timeout       | null                 | `3DS timeout`   | `auth_timeout`    | ☐      |
| Issuer decline     | `do_not_honor`       | null            | `issuer_decline`  | ☐      |
| Network error      | null                 | `network error` | `network`         | ☐      |
| Unknown            | `random_code`        | `random`        | `unknown`         | ☐      |

**Test Command**:

```bash
curl -X POST http://127.0.0.1:8000/v1/classify \
  -H "Content-Type: application/json" \
  -d '{"code": "insufficient_funds", "message": null}'
```

**Expected**: Returns category, recommendation, alt methods, optional cooldown

---

### 1.4 Recovery Link Generation (`/v1/recoveries`)

| Step | Action                 | Expected Result                    | Status |
| ---- | ---------------------- | ---------------------------------- | ------ |
| 1    | Create recovery link   | Returns token, URL, expires_at     | ☐      |
| 2    | Verify token is unique | Token is 22-char URL-safe string   | ☐      |
| 3    | Check expiry set       | expires_at is 24h from now         | ☐      |
| 4    | List recovery attempts | Returns array with created attempt | ☐      |

**Test Command**:

```bash
# Create link
curl -X POST http://127.0.0.1:8000/v1/recoveries/by_ref/TXN_TEST_001/link \
  -H "Content-Type: application/json" \
  -d '{"ttl_hours": 24, "channel": "email"}'

# List attempts
curl http://127.0.0.1:8000/v1/recoveries/by_ref/TXN_TEST_001
```

**Save the token from response for next tests**: ******\_\_\_******

---

### 1.5 Recovery Token Validation (`/v1/recoveries/by_token`)

| Test Case        | Endpoint                                       | Expected Behavior                  | Status |
| ---------------- | ---------------------------------------------- | ---------------------------------- | ------ |
| Valid token      | GET `/by_token/{valid_token}`                  | Returns ok=true, status, txn_ref   | ☐      |
| Invalid token    | GET `/by_token/invalid-xyz`                    | Returns ok=false, code=NOT_FOUND   | ☐      |
| Mark as opened   | POST `/by_token/{valid_token}/open`            | Status changes to "opened"         | ☐      |
| Idempotency test | POST `/by_token/{valid_token}/open` (2nd time) | Same response, opened_at unchanged | ☐      |
| Expired token    | GET `/by_token/{expired_token}`                | Returns ok=false, code=EXPIRED     | ☐      |

**Test Command**:

```bash
# Replace {TOKEN} with actual token from previous test
curl http://127.0.0.1:8000/v1/recoveries/by_token/{TOKEN}
curl -X POST http://127.0.0.1:8000/v1/recoveries/by_token/{TOKEN}/open
curl -X POST http://127.0.0.1:8000/v1/recoveries/by_token/{TOKEN}/open  # Test idempotency
```

---

### 1.6 Payment Endpoints (`/v1/payments`)

#### Note: These require STRIPE_SECRET_KEY environment variable

| Test Case             | Endpoint                | Expected (Without Stripe Config) | Status |
| --------------------- | ----------------------- | -------------------------------- | ------ |
| Create Payment Intent | POST `/stripe/intents`  | 503 "Stripe not configured"      | ☐      |
| Create Checkout       | POST `/stripe/checkout` | 503 "Stripe not configured"      | ☐      |

**Test Command**:

```bash
curl -X POST http://127.0.0.1:8000/v1/payments/stripe/intents \
  -H "Content-Type: application/json" \
  -d '{"transaction_ref": "TXN_TEST_001"}'
```

**With Stripe Configured**:
| Test Case | Expected Result | Status |
|-----------|----------------|--------|
| Create intent | Returns client_secret, payment_intent_id | ☐ |
| Create checkout | Returns checkout URL | ☐ |

---

### 1.7 Webhooks (`/v1/webhooks`)

| Test Case                           | Expected Behavior                     | Status |
| ----------------------------------- | ------------------------------------- | ------ |
| Stripe webhook without signature    | 400 or 503 error                      | ☐      |
| Stripe webhook with valid signature | Creates FailureEvent, returns ok=true | ☐      |

**Note**: Valid signature testing requires STRIPE_WEBHOOK_SECRET

---

## 2. FRONTEND APPLICATION

### 2.1 Public Pages (No Auth Required)

| Page     | URL        | Expected Content                       | Works | Notes |
| -------- | ---------- | -------------------------------------- | ----- | ----- |
| Homepage | `/`        | Welcome, Sign up/Sign in/Guest buttons | ☐     |       |
| Pricing  | `/pricing` | Pricing page loads                     | ☐     |       |
| Contact  | `/contact` | Contact form/info                      | ☐     |       |
| Privacy  | `/privacy` | Privacy policy                         | ☐     |       |
| Terms    | `/terms`   | Terms of service                       | ☐     |       |

**Browser Test**: Open http://localhost:3000 in browser

---

### 2.2 Authentication Flow

#### Sign In Page (`/auth/signin`)

| Step | Action                   | Expected Result                      | Status |
| ---- | ------------------------ | ------------------------------------ | ------ |
| 1    | Navigate to /auth/signin | Sign in form displays                | ☐      |
| 2    | Enter any email          | Input accepts email                  | ☐      |
| 3    | Enter any password       | Input accepts password               | ☐      |
| 4    | Click "Sign In"          | Redirects to /dashboard              | ☐      |
| 5    | Verify session           | Cookie `next-auth.session-token` set | ☐      |

**Note**: Current implementation accepts ANY credentials (demo mode)

#### Sign Up Page (`/auth/signup`)

| Step | Action                   | Expected Result           | Status |
| ---- | ------------------------ | ------------------------- | ------ |
| 1    | Navigate to /auth/signup | Sign up form displays     | ☐      |
| 2    | Fill form                | Form accepts input        | ☐      |
| 3    | Submit                   | Appropriate action occurs | ☐      |

---

### 2.3 Protected Routes (Require Authentication)

#### Test: Access Without Auth

| Page       | URL           | Expected Behavior        | Status |
| ---------- | ------------- | ------------------------ | ------ |
| Dashboard  | `/dashboard`  | Redirect to /auth/signin | ☐      |
| Onboarding | `/onboarding` | Redirect to /auth/signin | ☐      |
| Rules      | `/rules`      | Redirect to /auth/signin | ☐      |
| Templates  | `/templates`  | Redirect to /auth/signin | ☐      |
| Developer  | `/developer`  | Redirect to /auth/signin | ☐      |
| Settings   | `/settings`   | Redirect to /auth/signin | ☐      |

**Test Method**:

1. Open incognito/private browser window
2. Try accessing each URL directly
3. Verify redirect to signin with `callbackUrl` parameter

---

### 2.4 Dashboard Page (`/dashboard`)

**Prerequisites**: Sign in first

| Component               | Expected Content       | Status |
| ----------------------- | ---------------------- | ------ |
| Page title              | "Dashboard"            | ☐      |
| Total Recovered card    | Shows "$82.4K"         | ☐      |
| Active Rules card       | Shows "18"             | ☐      |
| Alerts card             | Shows "3"              | ☐      |
| Merchants card          | Shows "12"             | ☐      |
| Recent Activity section | Shows 3 activity items | ☐      |
| Next Steps section      | Shows 3 action items   | ☐      |

**Note**: Currently displays static mock data (no API integration)

---

### 2.5 Onboarding Page (`/onboarding`)

| Component             | Expected Content                  | Status |
| --------------------- | --------------------------------- | ------ |
| Page title            | "Onboarding"                      | ☐      |
| Checklist items       | Shows 3 tasks                     | ☐      |
| Task 1                | "Connect merchant data sources"   | ☐      |
| Task 2                | "Map customer identifiers"        | ☐      |
| Task 3                | "Schedule recovery automations"   | ☐      |
| Mark complete buttons | Buttons display for each task     | ☐      |
| Integrations section  | Shows "No integrations connected" | ☐      |

**Interactions to Test**:

- [ ] Click "View onboarding guide" button
- [ ] Click "Mark complete" buttons
- [ ] Click "Go to developer logs" button

---

### 2.6 Rules Page (`/rules`)

| Component     | Expected Content           | Status |
| ------------- | -------------------------- | ------ |
| Page title    | "Recovery Rules"           | ☐      |
| Rule 1        | "3-Day Follow-up" - Active | ☐      |
| Rule 2        | "7-Day Reminder" - Active  | ☐      |
| Rule 3        | "Final Notice" - Draft     | ☐      |
| Create button | "Create New Rule" button   | ☐      |

**Interactions to Test**:

- [ ] Click "Create New Rule" button
- [ ] Hover over rule cards

**Note**: Currently displays static rules (no API integration)

---

### 2.7 Templates Page (`/templates`)

| Component     | Expected Content                      | Status |
| ------------- | ------------------------------------- | ------ |
| Page title    | "Email Templates"                     | ☐      |
| Template 1    | "Payment Reminder" - Used 24 times    | ☐      |
| Template 2    | "Card Update Request" - Used 18 times | ☐      |
| Template 3    | "Final Notice" - Used 5 times         | ☐      |
| Edit buttons  | Each template has "Edit" button       | ☐      |
| Create button | "Create New Template" button          | ☐      |

**Interactions to Test**:

- [ ] Click "Edit" buttons
- [ ] Click "Create New Template" button

---

### 2.8 Developer Page (`/developer`)

| Component          | Expected Content                | Status |
| ------------------ | ------------------------------- | ------ |
| Page title         | "Developer Tools"               | ☐      |
| API Keys section   | Shows Production & Test keys    | ☐      |
| Production key     | "sk_live_abc123xyz789" (masked) | ☐      |
| Test key           | "sk_test_def456uvw012" (masked) | ☐      |
| Copy buttons       | Each key has copy button        | ☐      |
| Webhooks section   | "Configure webhook endpoints"   | ☐      |
| Add Webhook button | Button displays                 | ☐      |
| API Docs section   | Link to "docs.tinko.in"         | ☐      |

**Interactions to Test**:

- [ ] Click "Copy" buttons for API keys
- [ ] Click "Add Webhook" button
- [ ] Click "View Docs" link (opens in new tab)

---

### 2.9 Payer Recovery Flow (`/pay/retry/[token]`)

**Prerequisites**:

1. Backend running
2. Valid recovery token generated (from section 1.4)

| Step | Action                           | Expected Result                                     | Status |
| ---- | -------------------------------- | --------------------------------------------------- | ------ |
| 1    | Navigate to `/pay/retry/{TOKEN}` | Shows "Checking your link..."                       | ☐      |
| 2    | Wait for validation              | Shows "Payment recovery" page                       | ☐      |
| 3    | Verify content                   | Shows transaction ref, "Continue to payment" button | ☐      |
| 4    | Click button (demo mode)         | Redirects to success page after 800ms               | ☐      |
| 5    | Click button (real mode)         | Redirects to Stripe Checkout                        | ☐      |

**Test Invalid Token**:

- [ ] Navigate to `/pay/retry/invalid-token-xyz`
- [ ] Expected: "Invalid link" message

**Test Expired Token**:

- [ ] Create token with `ttl_hours: 0`
- [ ] Navigate to that token's URL
- [ ] Expected: "Link expired" message

**Environment Variable**:

```bash
# Demo mode (no Stripe API calls)
NEXT_PUBLIC_PAYMENTS_DEMO=true

# Real mode (requires Stripe)
NEXT_PUBLIC_PAYMENTS_DEMO=false
```

---

### 2.10 Navigation & Layout

| Component        | Expected Behavior       | Status |
| ---------------- | ----------------------- | ------ |
| Top navbar       | Displays on all pages   | ☐      |
| Sidebar          | Shows on console pages  | ☐      |
| User menu        | Shows user avatar/name  | ☐      |
| Org switcher     | Shows org selector      | ☐      |
| Navigation links | All links work          | ☐      |
| Sign out         | Signs out and redirects | ☐      |

**Navigation Links to Test**:

- [ ] Dashboard
- [ ] Onboarding
- [ ] Rules
- [ ] Templates
- [ ] Developer
- [ ] Settings

---

### 2.11 Responsive Design

| Device/Width     | Test                             | Status |
| ---------------- | -------------------------------- | ------ |
| Desktop (1920px) | All elements display correctly   | ☐      |
| Laptop (1366px)  | Layout adapts properly           | ☐      |
| Tablet (768px)   | Sidebar collapses/hamburger menu | ☐      |
| Mobile (375px)   | Cards stack vertically           | ☐      |

**Test Method**: Use browser DevTools responsive mode

---

## 3. INTEGRATION TESTS

### 3.1 End-to-End Recovery Flow

| Step | Action                              | Expected Result             | Status |
| ---- | ----------------------------------- | --------------------------- | ------ |
| 1    | POST payment_failed event (backend) | Event created               | ☐      |
| 2    | POST recovery link (backend)        | Token generated             | ☐      |
| 3    | Open payer URL (frontend)           | Page loads, token validated | ☐      |
| 4    | Click continue (frontend)           | Payment flow initiates      | ☐      |
| 5    | Complete payment                    | Success callback            | ☐      |

---

### 3.2 Cross-Origin Requests (CORS)

| Test                       | Expected Result                         | Status |
| -------------------------- | --------------------------------------- | ------ |
| Frontend calls backend API | Requests succeed (CORS headers present) | ☐      |
| Preflight OPTIONS requests | Returns 200 with correct headers        | ☐      |

**Check in DevTools**: Network tab should show no CORS errors

---

## 4. ERROR HANDLING

### 4.1 Backend Error Responses

| Scenario               | Expected Response          | Status |
| ---------------------- | -------------------------- | ------ |
| Invalid JSON payload   | 422 Unprocessable Entity   | ☐      |
| Missing required field | 422 with validation errors | ☐      |
| Resource not found     | 404 Not Found              | ☐      |
| Internal server error  | 500 with error details     | ☐      |

---

### 4.2 Frontend Error States

| Scenario        | Expected UI                       | Status |
| --------------- | --------------------------------- | ------ |
| Backend offline | Error message displayed           | ☐      |
| Network timeout | Loading state → error message     | ☐      |
| Invalid token   | Clear error message on payer page | ☐      |

---

## 5. SECURITY CHECKS

| Check                     | Expected Behavior                     | Status |
| ------------------------- | ------------------------------------- | ------ |
| Protected routes redirect | Unauthenticated access → /auth/signin | ☐      |
| Session cookies           | HttpOnly, Secure flags set            | ☐      |
| CORS policy               | Only allowed origins accepted         | ☐      |
| XSS protection            | Headers include X-XSS-Protection      | ☐      |
| Frame protection          | X-Frame-Options: DENY                 | ☐      |

---

## 6. PERFORMANCE CHECKS

| Metric                         | Target  | Actual | Status |
| ------------------------------ | ------- | ------ | ------ |
| Homepage load time             | < 2s    | \_\_\_ | ☐      |
| Dashboard load time            | < 2s    | \_\_\_ | ☐      |
| API response time (health)     | < 100ms | \_\_\_ | ☐      |
| API response time (classifier) | < 200ms | \_\_\_ | ☐      |

---

## 7. BROWSER COMPATIBILITY

| Browser | Version | Status |
| ------- | ------- | ------ |
| Chrome  | Latest  | ☐      |
| Firefox | Latest  | ☐      |
| Edge    | Latest  | ☐      |
| Safari  | Latest  | ☐      |

---

## 8. KNOWN LIMITATIONS (Expected Failures)

### Backend

- ✓ No actual retry automation (Celery not implemented)
- ✓ No email/SMS notifications (SMTP/Twilio not configured)
- ✓ Stripe endpoints fail without API keys
- ✓ No user authentication (accepts any credentials)
- ✓ No org-level data isolation
- ✓ Rules are hardcoded (not DB-driven)

### Frontend

- ✓ Dashboard shows static data (no API integration)
- ✓ Rules page shows static rules (no CRUD)
- ✓ Templates page shows static templates (no editor)
- ✓ No real user registration
- ✓ No role-based access control enforcement
- ✓ No analytics charts with real data

---

## 9. MANUAL SMOKE TEST SCRIPT

```bash
# Terminal 1: Start backend
cd Stealth-Reecovery
C:/Python313/python.exe -m uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd Stealth-Reecovery/tinko-console
npm run dev

# Terminal 3: Run automated tests
cd Stealth-Reecovery
C:/Python313/python.exe test_all_endpoints.py

# Browser: Open and test
# 1. http://localhost:3000 - Homepage
# 2. Sign in with any credentials
# 3. Navigate through all menu items
# 4. Test payer recovery flow with generated token
```

---

## SIGN-OFF

| Role      | Name | Signature | Date |
| --------- | ---- | --------- | ---- |
| Tester    |      |           |      |
| Developer |      |           |      |
| QA Lead   |      |           |      |

---

## NOTES & ISSUES FOUND

_Use this space to document any bugs, unexpected behavior, or improvement suggestions:_

```
Issue #1:


Issue #2:


Issue #3:

```

---

**End of Test Checklist**
