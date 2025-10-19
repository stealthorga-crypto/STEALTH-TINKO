# TINKO RECOVERY — GAP-TO-DONE EXECUTION PLAN

**Audit Date:** October 19, 2025  
**Session:** 20251019-115205  
**Planning Methodology:** Phased delivery with dependencies mapped

---

## PHASE 0: FOUNDATION & QUICK WINS (1-2 days)

**Objective:** Fix critical bugs and wire existing UI to backend APIs

### Task 0.1: Fix Stripe Test Mock Issue

**Priority:** P0  
**Estimate:** S (5 minutes)  
**Dependencies:** None

**Why it matters:**  
Blocks 100% test coverage; prevents CI from being fully green.

**Deliverables:**

- Update `tests/test_stripe_integration.py` line 181
- Change `stripe.error.InvalidRequestError` → `stripe.StripeError`

**Acceptance Criteria:**

- [ ] All 43 tests passing (100%)
- [ ] CI pipeline green

**Files to Modify:**

```
tests/test_stripe_integration.py:181
```

**Rollback Notes:**  
Revert commit; test change is isolated.

---

### Task 0.2: Wire Dashboard Analytics API

**Priority:** P1  
**Estimate:** S (2-3 hours)  
**Dependencies:** None

**Why it matters:**  
Dashboard currently shows mock data; real-time KPIs are available but not connected.

**Deliverables:**

- Connect KPI cards to `/v1/analytics/*` endpoints
- Replace mock data with React Query API calls
- Add loading/error states

**Files to Modify:**

```
tinko-console/app/(console)/dashboard/page.tsx
tinko-console/app/(console)/dashboard/_components/recovery-feed.tsx
```

**Implementation Checklist:**

- [ ] Import `useQuery` from `@tanstack/react-query`
- [ ] Create API calls to:
  - `GET /v1/analytics/recovery_rate`
  - `GET /v1/analytics/revenue_recovered`
  - `GET /v1/analytics/failure_categories`
  - `GET /v1/analytics/attempts_by_channel`
- [ ] Remove mock data constants
- [ ] Handle loading states with skeleton loaders
- [ ] Handle error states with retry buttons
- [ ] Add time-period filter (7d, 30d, 90d)

**Acceptance Criteria:**

- [ ] KPI cards show real data from backend
- [ ] Charts render live data (not mock)
- [ ] Loading states appear during fetch
- [ ] Error messages display on API failure
- [ ] Time filter updates data correctly

**Rollback Notes:**  
Revert commit; UI reverts to mock data gracefully.

---

### Task 0.3: Add Rate Limiting to Auth Endpoints

**Priority:** P1  
**Estimate:** S (4-6 hours)  
**Dependencies:** None

**Why it matters:**  
Prevents brute-force attacks on login/registration; security best practice.

**Deliverables:**

- Install `slowapi` library
- Configure rate limiting on auth routes
- Add Redis-backed rate limiter

**Files to Create/Modify:**

```
requirements.txt (add slowapi>=0.1.9)
app/main.py (add slowapi middleware)
app/routers/auth.py (apply rate limit decorators)
```

**Implementation Checklist:**

- [ ] Add `slowapi>=0.1.9` to `requirements.txt`
- [ ] Install: `pip install slowapi`
- [ ] Configure in `app/main.py`:

  ```python
  from slowapi import Limiter, _rate_limit_exceeded_handler
  from slowapi.util import get_remote_address
  from slowapi.errors import RateLimitExceeded

  limiter = Limiter(key_func=get_remote_address, storage_uri=os.getenv("REDIS_URL"))
  app.state.limiter = limiter
  app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
  ```

- [ ] Apply to auth routes:
  ```python
  @router.post("/login")
  @limiter.limit("5/minute")  # 5 attempts per minute
  async def login(...):
  ```
- [ ] Add tests: `tests/test_rate_limiting.py`

**Acceptance Criteria:**

- [ ] Login limited to 5 requests/minute per IP
- [ ] Register limited to 3 requests/minute per IP
- [ ] 429 status returned on rate limit exceeded
- [ ] Redis stores rate limit state
- [ ] Tests verify rate limiting behavior

**Rollback Notes:**  
Remove slowapi middleware and decorators; no DB changes.

---

## PHASE 1: PAYMENTS CORE ENHANCEMENTS (2-3 days)

**Objective:** Complete multi-PSP support and improve notification UX

### Task 1.1: Complete Razorpay Integration

**Priority:** P1  
**Estimate:** M (2 days)  
**Dependencies:** None

**Why it matters:**  
Razorpay is critical for Indian market; currently stubbed but not functional.

**Deliverables:**

- Complete Razorpay adapter implementation
- Add Razorpay router with endpoints
- Add Razorpay webhook handling
- Add tests for Razorpay flow

**Files to Create/Modify:**

```
app/psp/razorpay_adapter.py (complete implementation)
app/routers/payments_razorpay.py (NEW)
app/routers/webhooks_razorpay.py (NEW)
tests/test_payments_razorpay.py (NEW)
tests/test_webhooks_razorpay.py (NEW)
.env.example (add RAZORPAY_* variables)
```

**Implementation Checklist:**

- [ ] Complete `app/psp/razorpay_adapter.py`:
  - `create_order(amount, currency, receipt, notes)` → returns order_id
  - `verify_signature(payload, signature, secret)` → boolean
- [ ] Create `app/routers/payments_razorpay.py`:
  - `POST /v1/payments/razorpay/orders` → create Razorpay order
  - `GET /v1/payments/razorpay/orders/{order_id}` → fetch order status
- [ ] Create `app/routers/webhooks_razorpay.py`:
  - `POST /v1/webhooks/razorpay` → handle payment.authorized, payment.failed events
- [ ] Update `app/main.py`: include razorpay routers
- [ ] Add tests with mocked Razorpay SDK
- [ ] Update frontend payer page to support Razorpay Checkout

**Acceptance Criteria:**

- [ ] Razorpay order creation works with test credentials
- [ ] Webhook signature verification passes
- [ ] Transaction status updates on webhook events
- [ ] Tests pass (10+ tests expected)
- [ ] Frontend can embed Razorpay Checkout modal

**Rollback Notes:**  
Remove routers from `main.py`; no DB changes.

---

### Task 1.2: Implement HTML Email Templates

**Priority:** P1  
**Estimate:** M (1 day)  
**Dependencies:** None

**Why it matters:**  
Professional email UX; higher click-through rates on recovery links.

**Deliverables:**

- HTML email templates with responsive design
- Template variable substitution engine
- Preview endpoint for testing

**Files to Create:**

```
app/templates/email/recovery_link.html (NEW)
app/templates/email/base.html (NEW)
app/services/email_renderer.py (NEW)
app/routers/dev.py (add preview endpoint)
```

**Implementation Checklist:**

- [ ] Create `app/templates/email/base.html`:
  - Responsive design (mobile-first)
  - Brand colors and logo
  - Footer with unsubscribe link
- [ ] Create `app/templates/email/recovery_link.html`:
  - CTA button with recovery link
  - Transaction details (amount, currency, merchant)
  - Expiry time countdown
- [ ] Create `app/services/email_renderer.py`:

  ```python
  from jinja2 import Environment, FileSystemLoader

  def render_template(template_name, context):
      env = Environment(loader=FileSystemLoader('app/templates'))
      template = env.get_template(template_name)
      return template.render(context)
  ```

- [ ] Update `app/tasks/notification_tasks.py`:
  - Use `email_renderer.render_template()` instead of plaintext
- [ ] Add preview endpoint: `GET /v1/dev/email-preview/{template_name}`
- [ ] Test with MailHog

**Acceptance Criteria:**

- [ ] HTML email renders correctly in Gmail, Outlook, Apple Mail
- [ ] CTA button is prominent and clickable
- [ ] Variables substituted correctly (amount, link, expiry)
- [ ] Preview endpoint shows rendered HTML
- [ ] Email passes spam filter tests (mail-tester.com)

**Rollback Notes:**  
Revert to plaintext emails; template files can be deleted.

---

### Task 1.3: Implement Password Reset Flow

**Priority:** P2  
**Estimate:** M (1 day)  
**Dependencies:** Task 1.2 (email templates)

**Why it matters:**  
Users cannot recover lost passwords; common support request.

**Deliverables:**

- Password reset request endpoint
- Reset token generation and validation
- Reset password endpoint
- Email notification

**Files to Create/Modify:**

```
app/routers/auth.py (add reset endpoints)
app/models.py (add PasswordResetToken model - optional, use JWT)
app/templates/email/password_reset.html (NEW)
tinko-console/app/auth/reset-password/page.tsx (NEW)
tests/test_password_reset.py (NEW)
```

**Implementation Checklist:**

- [ ] Add `POST /v1/auth/forgot-password`:
  - Input: `{email}`
  - Generate JWT reset token (15 min expiry)
  - Send email with reset link
- [ ] Add `POST /v1/auth/reset-password`:
  - Input: `{token, new_password}`
  - Verify token
  - Hash new password
  - Update user record
- [ ] Create frontend page: `tinko-console/app/auth/reset-password/page.tsx`
  - Form with token (from URL) and new password fields
  - Call backend API
  - Redirect to login on success
- [ ] Create email template: `app/templates/email/password_reset.html`
- [ ] Add tests for token generation, validation, expiry

**Acceptance Criteria:**

- [ ] User receives reset email within 1 minute
- [ ] Reset link expires after 15 minutes
- [ ] Password updated successfully
- [ ] Old password no longer works
- [ ] Tokens are single-use
- [ ] Tests cover edge cases (expired token, invalid token, user not found)

**Rollback Notes:**  
Remove endpoints and frontend page; no migration needed if using JWT.

---

## PHASE 2: ANALYTICS & DASHBOARD (2 days)

**Objective:** Complete analytics layer and add missing visualizations

### Task 2.1: Add Trend Analytics Endpoint

**Priority:** P2  
**Estimate:** M (4-6 hours)  
**Dependencies:** None

**Why it matters:**  
Dashboard needs time-series data for line charts; currently only aggregates available.

**Deliverables:**

- New endpoint for trend data (time-series)
- SQL queries with group by date
- Tests for aggregation logic

**Files to Create/Modify:**

```
app/routers/analytics.py (add new endpoint)
app/services/analytics.py (add trend query)
tests/test_analytics.py (NEW)
```

**Implementation Checklist:**

- [ ] Add `GET /v1/analytics/trend`:
  - Query params: `org_id`, `period` (7d, 30d, 90d), `metric` (attempts|recovered|revenue)
  - Returns: `[{date, value}]` array for charting
- [ ] Implement SQL in `app/services/analytics.py`:
  ```python
  def get_trend_data(org_id, period, metric):
      # GROUP BY DATE(created_at)
      # Aggregate: COUNT(*) or SUM(amount)
      # Filter by org_id and date range
      pass
  ```
- [ ] Add tests with seeded time-series data
- [ ] Update frontend dashboard to call this endpoint
- [ ] Render Recharts LineChart with trend data

**Acceptance Criteria:**

- [ ] Endpoint returns correct daily aggregates
- [ ] Data is sorted by date (oldest to newest)
- [ ] Frontend line chart renders trend
- [ ] Tests verify aggregation logic
- [ ] Performance: query runs in <200ms for 90d period

**Rollback Notes:**  
Remove endpoint; frontend reverts to showing only KPIs.

---

### Task 2.2: Add Export Functionality

**Priority:** P2  
**Estimate:** S (4 hours)  
**Dependencies:** None

**Why it matters:**  
Users need to export data for reporting and analysis.

**Deliverables:**

- CSV export endpoint for transactions
- CSV export endpoint for recovery attempts
- Download button in frontend

**Files to Create/Modify:**

```
app/routers/exports.py (NEW)
tinko-console/app/(console)/dashboard/page.tsx (add export button)
```

**Implementation Checklist:**

- [ ] Create `app/routers/exports.py`:
  - `GET /v1/exports/transactions.csv?org_id=&period=`
  - `GET /v1/exports/recovery_attempts.csv?org_id=&period=`
  - Use Python `csv` module
  - Stream response for large datasets
- [ ] Add to `app/main.py`: `app.include_router(exports_router, prefix="/v1/exports")`
- [ ] Add export button to dashboard:
  ```tsx
  <Button onClick={() => downloadCSV("/v1/exports/transactions.csv")}>
    Export CSV
  </Button>
  ```
- [ ] Implement `downloadCSV()` helper in `tinko-console/lib/utils.ts`

**Acceptance Criteria:**

- [ ] CSV downloads with correct headers and data
- [ ] Large datasets (10k+ rows) stream without timeout
- [ ] Filename includes date: `transactions_2025-10-19.csv`
- [ ] Excel can open CSV without encoding issues (UTF-8 BOM)

**Rollback Notes:**  
Remove export router; frontend button can be hidden.

---

## PHASE 3: INFRASTRUCTURE & OBSERVABILITY (3 days)

**Objective:** Production-grade deployment and monitoring

### Task 3.1: Add Prometheus Metrics Endpoint

**Priority:** P2  
**Estimate:** S (1 day)  
**Dependencies:** None

**Why it matters:**  
Grafana dashboards require `/metrics` endpoint; current observability is Sentry-only.

**Deliverables:**

- Prometheus metrics endpoint
- Custom metrics for business KPIs
- Grafana dashboard JSON

**Files to Create/Modify:**

```
requirements.txt (add prometheus-fastapi-instrumentator)
app/main.py (add metrics endpoint)
grafana/dashboards/tinko-recovery.json (NEW)
```

**Implementation Checklist:**

- [ ] Add `prometheus-fastapi-instrumentator>=7.0.0` to requirements
- [ ] Install: `pip install prometheus-fastapi-instrumentator`
- [ ] Configure in `app/main.py`:

  ```python
  from prometheus_fastapi_instrumentator import Instrumentator

  Instrumentator().instrument(app).expose(app, endpoint="/metrics")
  ```

- [ ] Add custom metrics:

  ```python
  from prometheus_client import Counter, Histogram

  recovery_attempts_total = Counter('recovery_attempts_total', 'Total recovery attempts', ['org_id', 'channel'])
  payment_amount = Histogram('payment_amount', 'Payment amounts', ['currency'])
  ```

- [ ] Create Grafana dashboard JSON: `grafana/dashboards/tinko-recovery.json`
  - Panel: Request rate (QPS)
  - Panel: Latency (p50, p95, p99)
  - Panel: Error rate (5xx responses)
  - Panel: Recovery rate (custom metric)
- [ ] Update `docker-compose.yml`: add Prometheus + Grafana services

**Acceptance Criteria:**

- [ ] `/metrics` endpoint returns Prometheus format
- [ ] Grafana dashboard displays request metrics
- [ ] Custom business metrics visible (recovery rate, payment volume)
- [ ] Alerts configured for high error rate (>5%)

**Rollback Notes:**  
Remove instrumentator from `main.py`; Prometheus services can be stopped.

---

### Task 3.2: Complete Kubernetes Manifests

**Priority:** P2  
**Estimate:** M (2 days)  
**Dependencies:** None

**Why it matters:**  
Current HPA cannot work without Deployment/Service; need full k8s setup for production.

**Deliverables:**

- Deployment manifests for 3 services
- Service manifests with load balancing
- Ingress configuration with TLS
- ConfigMap and Secret manifests

**Files to Create:**

```
k8s/deployment-backend.yml (NEW)
k8s/deployment-frontend.yml (NEW)
k8s/deployment-worker.yml (NEW)
k8s/service-backend.yml (NEW)
k8s/service-frontend.yml (NEW)
k8s/ingress.yml (NEW)
k8s/configmap.yml (NEW)
k8s/secrets.yml.example (NEW)
k8s/README.md (deployment guide)
```

**Implementation Checklist:**

- [ ] Create Deployment for backend:
  - Image: `tinko/backend:latest`
  - Replicas: 2 (HPA will scale)
  - Env vars from ConfigMap/Secret
  - Health checks: `/healthz`, `/readyz`
  - Resources: requests (500m CPU, 512Mi RAM), limits (1 CPU, 1Gi RAM)
- [ ] Create Deployment for frontend:
  - Image: `tinko/frontend:latest`
  - Replicas: 2
- [ ] Create Deployment for worker:
  - Image: `tinko/backend:latest`
  - Command: `celery -A app.worker worker`
  - Replicas: 2
- [ ] Create Services (ClusterIP):
  - `tinko-backend` → port 8000
  - `tinko-frontend` → port 3000
- [ ] Create Ingress:
  - Host: `api.tinko.in` → backend service
  - Host: `console.tinko.in` → frontend service
  - TLS cert from cert-manager (Let's Encrypt)
- [ ] Create ConfigMap: non-sensitive env vars
- [ ] Create Secret example: `kubectl create secret generic tinko-secrets --from-literal=...`
- [ ] Update `k8s/hpa.yml` to reference new deployments
- [ ] Write deployment guide: `k8s/README.md`

**Acceptance Criteria:**

- [ ] `kubectl apply -k k8s/` deploys all resources
- [ ] Backend pods start and pass health checks
- [ ] Frontend accessible at https://console.tinko.in
- [ ] API accessible at https://api.tinko.in
- [ ] HPA scales pods based on CPU load
- [ ] TLS certificates auto-renew
- [ ] Secrets not committed to git

**Rollback Notes:**  
`kubectl delete -k k8s/`; no persistent data loss if DB is external.

---

## PHASE 4: QUALITY & TESTING (5 days)

**Objective:** Comprehensive test coverage for frontend and E2E flows

### Task 4.1: Add Frontend Unit Tests

**Priority:** P1  
**Estimate:** L (3 days)  
**Dependencies:** None

**Why it matters:**  
Frontend has zero test coverage; cannot confidently refactor or deploy.

**Deliverables:**

- Vitest + React Testing Library setup
- Component tests for critical pages
- API integration tests

**Files to Create:**

```
tinko-console/vitest.config.ts (NEW)
tinko-console/app/(console)/dashboard/__tests__/page.test.tsx (NEW)
tinko-console/app/(console)/rules/__tests__/page.test.tsx (NEW)
tinko-console/app/pay/retry/__tests__/[token].test.tsx (NEW)
tinko-console/lib/__tests__/api.test.ts (NEW)
```

**Implementation Checklist:**

- [ ] Install dependencies:
  ```bash
  npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
  ```
- [ ] Create `vitest.config.ts`:

  ```typescript
  import { defineConfig } from "vitest/config";
  import react from "@vitejs/plugin-react";

  export default defineConfig({
    plugins: [react()],
    test: {
      environment: "jsdom",
      globals: true,
      setupFiles: "./test-setup.ts",
    },
  });
  ```

- [ ] Write component tests:
  - Dashboard: renders KPI cards, handles loading/error
  - Rules page: form validation, API calls, CRUD operations
  - Payment page: Stripe Elements integration, success flow
- [ ] Write API tests:
  - `lib/api.ts`: mock fetch, test error handling
- [ ] Add npm script: `"test": "vitest"`
- [ ] Update CI: `.github/workflows/ci.yml` add `npm run test`

**Acceptance Criteria:**

- [ ] 80%+ code coverage for components
- [ ] All critical user flows tested
- [ ] Tests run in CI
- [ ] Tests complete in <60 seconds
- [ ] Mocked API calls (no real backend needed)

**Rollback Notes:**  
Remove vitest config and test files; no impact on app.

---

### Task 4.2: Add E2E Tests with Playwright

**Priority:** P1  
**Estimate:** M (2 days)  
**Dependencies:** Task 4.1 (frontend tests)

**Why it matters:**  
E2E tests catch integration issues and validate full user journeys.

**Deliverables:**

- Playwright test specs for critical flows
- CI integration
- Test reporting

**Files to Create:**

```
tinko-console/tests/e2e/auth.spec.ts (NEW)
tinko-console/tests/e2e/dashboard.spec.ts (NEW)
tinko-console/tests/e2e/payment.spec.ts (NEW)
tinko-console/tests/e2e/rules.spec.ts (NEW)
```

**Implementation Checklist:**

- [ ] Write E2E specs:
  - **Auth flow:** Sign up → verify email → login → dashboard
  - **Dashboard:** View KPIs, filter by period, export CSV
  - **Payment flow:** Click recovery link → complete checkout → see success page
  - **Rules CRUD:** Create policy → edit → delete → verify in list
- [ ] Configure Playwright for multiple browsers (Chromium, Firefox, WebKit)
- [ ] Add test users/data seeding script
- [ ] Run against local `docker-compose up` stack
- [ ] Add npm script: `"test:e2e": "playwright test"`
- [ ] Update CI: add E2E test job (runs after build)

**Acceptance Criteria:**

- [ ] 10+ E2E scenarios covered
- [ ] Tests pass on Chromium, Firefox, WebKit
- [ ] CI runs E2E tests on every PR
- [ ] Test report generated (HTML + screenshots on failure)
- [ ] Flaky tests debugged and stabilized

**Rollback Notes:**  
Remove test specs; Playwright config remains for future use.

---

## DEPENDENCIES GRAPH

```
Phase 0: Foundation (1-2 days)
├─ Task 0.1: Fix Stripe Test Mock (5 min) [NO DEPS]
├─ Task 0.2: Wire Dashboard API (3 hr) [NO DEPS]
└─ Task 0.3: Rate Limiting (6 hr) [NO DEPS]

Phase 1: Payments (2-3 days)
├─ Task 1.1: Razorpay Integration (2 days) [NO DEPS]
├─ Task 1.2: HTML Email Templates (1 day) [NO DEPS]
└─ Task 1.3: Password Reset (1 day) [DEPENDS ON Task 1.2]

Phase 2: Analytics (2 days)
├─ Task 2.1: Trend Endpoint (6 hr) [NO DEPS]
└─ Task 2.2: CSV Export (4 hr) [NO DEPS]

Phase 3: Infrastructure (3 days)
├─ Task 3.1: Prometheus Metrics (1 day) [NO DEPS]
└─ Task 3.2: K8s Manifests (2 days) [NO DEPS]

Phase 4: Testing (5 days)
├─ Task 4.1: Frontend Unit Tests (3 days) [NO DEPS]
└─ Task 4.2: E2E Tests (2 days) [DEPENDS ON Task 4.1]
```

---

## ESTIMATION SUMMARY

| Phase     | Total Days     | Critical Path | Parallelizable                           |
| --------- | -------------- | ------------- | ---------------------------------------- |
| Phase 0   | 1-2            | 1 day         | Yes (all 3 tasks)                        |
| Phase 1   | 2-3            | 3 days        | Partially (1.1 + 1.2 parallel, then 1.3) |
| Phase 2   | 2              | 1 day         | Yes (both tasks)                         |
| Phase 3   | 3              | 2 days        | Yes (both tasks)                         |
| Phase 4   | 5              | 5 days        | Sequential (4.2 depends on 4.1)          |
| **TOTAL** | **13-15 days** | **12 days**   | With 2 devs: 8-10 days                   |

---

## RECOMMENDED EXECUTION ORDER

**Sprint 1 (Week 1): Foundation + Payments**

- Day 1: Phase 0 (all tasks)
- Day 2-3: Task 1.1 (Razorpay) + Task 1.2 (Email templates) in parallel
- Day 4: Task 1.3 (Password reset)

**Sprint 2 (Week 2): Analytics + Infrastructure**

- Day 5: Phase 2 (both tasks in parallel)
- Day 6-8: Phase 3 (both tasks in parallel)

**Sprint 3 (Week 3): Testing**

- Day 9-11: Task 4.1 (Frontend unit tests)
- Day 12-13: Task 4.2 (E2E tests)

**Total Timeline:** 13 days with 1 developer, **8-10 days with 2 developers**

---

**End of Gap-to-Done Plan**
