## FULL BUILD PLAN — Tinko Recovery Platform

---

## Section 1: Executive Summary

Current repository snapshot

- Current branch: main
- Audit-derived completion: ~87% (per PROJECT_STATUS_SUMMARY.md)
- Total modules to finish: 19 (listed in plan)

Objective

- Turn the project from ~87% → 100% production-ready by completing all pending modules across Frontend, Backend, Data & Analytics and DevOps.
- Target timeline (focused run): 2 weeks for MVP-to-prod readiness; detailed per-phase estimates below.

High-level estimates

- Total estimated engineering hours: 90-140h
- Minimal critical path (Celery, Notifications, RBAC, Razorpay, Rules UI): ~40 hours

Success criteria (MVP)

- All 19 modules either implemented or scaffolded with TODOs and tests added.
- Tests pass ≥ 95% on CI (local target ≥ 90% during work).
- CI pipeline builds images, runs lint, tests and can deploy to staging.

---

## Section 2: Phase Roadmap

| Phase | Scope               | Modules | Estimated Time | Goal                                |
| ----- | ------------------- | ------- | -------------- | ----------------------------------- |
| 1     | Frontend Completion | 1–4     | 10 h           | Merchant Console UI done            |
| 2     | Customer Experience | 5–7     | 8 h            | Payer flow functional               |
| 3     | Backend Core        | 8–13    | 18 h           | Retry engine + reconciliation ready |
| 4     | Data & Analytics    | 14–15   | 8 h            | Streaming + pruning active          |
| 5     | Infra & DevOps      | 16–19   | 10 h           | CI/CD & autoscaling ready           |

Notes:

- Estimates assume 1 full-stack engineer with repository familiarity. Times are approximate and include tests + basic docs.

---

## Section 3: Implementation Tasks (Modules 1–19)

For each module below: Goal, Files to create/edit, Dependencies/Required Vars, Acceptance Criteria, CLI Commands (branch + commit template). All file paths are relative to repo root.

---

Module 1 — Auth & Org Model
Goal: Add SSO + role-based access control (Admin / Owner / Viewer), API keys and refresh-token rotation.
Files to create/edit:

- app/routers/auth.py (edit - add RBAC endpoints)
- app/deps.py (edit - add require_role and api_key dependency)
- app/models.py (edit - role, permission, api_key models)
- app/services/auth_sso.py (new)
- tinko-console/app/(console)/auth/\* (frontend: signin/signup + SSO UI)
  Dependencies / Required Vars:
- NEXTAUTH_SECRET, JWT_SECRET, OAUTH_GOOGLE_CLIENT_ID, OAUTH_GOOGLE_CLIENT_SECRET
  Acceptance Criteria ✅:
- ✅ Users can sign in via SSO (Google) and local email/password.
- ✅ RBAC decorator `require_role(['admin'])` enforces access on admin endpoints.
- ✅ API keys usable to authenticate partner requests (header: X-API-KEY).
- ✅ Refresh token rotation implemented and tested.
  CLI Commands:
- git checkout -b feature/auth-rbac
- git add -A && git commit -m "feat(auth): add RBAC decorators, SSO scaffold"

---

Module 2 — Onboarding Wizard
Goal: Build an onboarding UI that captures PSP keys (Stripe/Razorpay) and retry policy defaults.
Files:

- tinko-console/app/(console)/settings/onboarding/page.tsx (new)
- app/routers/onboarding.py (new)
- app/services/onboarding_service.py (new)
  Dependencies / Required Vars:
- NEXT_PUBLIC_API_URL, STRIPE_SECRET_KEY, RAZORPAY_KEY_ID
  Acceptance Criteria ✅:
- ✅ Onboarding flow stores PSP credentials encrypted (or in database secrets table).
- ✅ Admin can set default retry policies from UI and verify PSP keys via test call.
  CLI Commands:
- git checkout -b feature/onboarding-wizard
- git commit -m "feat(onboarding): add onboarding wizard UI + backend endpoint"

---

Module 3 — Rules Editor
Goal: Provide a visual CRUD builder for retry logic (conditions/actions) with versioning.
Files:

- tinko-console/components/rules/rule-builder.tsx (new)
- tinko-console/app/(console)/rules/page.tsx (edit)
- app/routers/rules.py (new)
- app/services/rules_engine.py (new/edit)
- app/models.py (edit - Rule, RuleCondition, RuleAction models)
  Dependencies / Required Vars:
- RULES_DEFAULT_MAX_DEPTH (optional), DATABASE_URL
  Acceptance Criteria ✅:
- ✅ Save/edit/delete rules via API.
- ✅ Execution engine evaluates saved rules against transaction context.
- ✅ Rules have versions and a simple tester UI.
  CLI Commands:
- git checkout -b feature/rules-editor
- git commit -m "feat(rules): add UI and rules engine scaffold"

---

Module 4 — Dashboard Charts
Goal: Wire live data from `/v1/analytics/*` endpoints into dashboard charts.
Files:

- tinko-console/components/charts/\* (edit/create wrappers)
- tinko-console/app/(console)/dashboard/page.tsx (edit)
- app/routers/analytics.py (edit - ensure endpoints exist)
  Dependencies / Required Vars:
- NEXT_PUBLIC_API_URL
  Acceptance Criteria ✅:
- ✅ Charts call live endpoints, display real values and loading/error states.
- ✅ Refresh interval configurable (30–60s) in UI.
  CLI Commands:
- git checkout -b feature/dashboard-charts
- git commit -m "feat(dashboard): wire analytics endpoints to charts"

---

Module 5 — PSP Elements Integration
Goal: Tokenize card / UPI via Stripe + Razorpay on payment pages (secure elements).
Files:

- tinko-console/lib/stripe.ts (edit)
- tinko-console/lib/razorpay.ts (new)
- tinko-console/app/pay/checkout/page.tsx (edit)
- app/psp/stripe_adapter.py (ensure secure tokenization flow)
- app/psp/razorpay_adapter.py (edit/test)
  Dependencies / Required Vars:
- NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY, RAZORPAY_KEY_ID
  Acceptance Criteria ✅:
- ✅ Customer can enter card/UPI data in frontend without it hitting backend (tokenize in client).
- ✅ Frontend receives token and sends it to backend for payment creation.
- ✅ Tests for token flow (unit/integration stubs) present.
  CLI Commands:
- git checkout -b feature/psp-elements
- git commit -m "feat(psp): add frontend tokenization flows (Stripe/Razorpay)"

---

Module 6 — Retry Schedule Picker
Goal: UI component to pick smart retry windows (dayparting, business hours) and attach to policies.
Files:

- tinko-console/components/retry/schedule-picker.tsx (new)
- tinko-console/app/(console)/settings/retry-policies/page.tsx (edit)
- app/models.py (edit - RetryPolicy schedule fields)
  Dependencies / Required Vars:
- none specific; uses timezone configs
  Acceptance Criteria ✅:
- ✅ Admin sets windows, which are persisted and used by the scheduler.
- ✅ Picker supports timezone selection and presets (daily, business-hours, weekends).
  CLI Commands:
- git checkout -b feature/retry-schedule-picker
- git commit -m "feat(ui): add retry schedule picker and attach to policies"

---

Module 7 — i18n & Help Copy
Goal: Add Tamil / Hindi translations and FAQ content to frontend; internationalize components.
Files:

- tinko-console/i18n/en.json (edit)
- tinko-console/i18n/hi.json (new)
- tinko-console/i18n/ta.json (new)
- tinko-console/components/i18n/provider.tsx (edit/create)
- tinko-console/app/(console)/help/faq/page.tsx (edit)
  Dependencies / Required Vars:
- NEXT_PUBLIC_DEFAULT_LOCALE
  Acceptance Criteria ✅:
- ✅ UI shows language selector; translations for critical pages available.
- ✅ FAQ content populated for hi/ta.
  CLI Commands:
- git checkout -b feature/i18n-hi-ta
- git commit -m "feat(i18n): add Hindi and Tamil translations and FAQ pages"

---

Module 8 — Classifier
Goal: Implement soft/hard failure logic (rules engine) that categorizes payment failures and returns confidence scores.
Files to create/edit:

- app/services/classifier.py (create/edit)
- app/routers/classifier.py (ensure router exists)
- tests/test_classifier.py (update/add tests)
  Dependencies / Required Vars:
- PAYMENT_FAILURE_RULES (env or DB table)
  Acceptance Criteria ✅:
- ✅ Classifier returns category and confidence for sample events.
- ✅ Classifier is exercised by unit tests (>= 90% pass for classifier tests).
  CLI Commands:
- git checkout -b feature/classifier
- git commit -m "feat(classifier): add classify_failure skeleton and tests"

---

Module 9 — Retry Engine
Goal: Auto-retry routing based on policy table with exponential backoff, backfill support and idempotency.
Files:

- app/services/retry_engine.py (new)
- app/tasks/retry_tasks.py (edit - wire in engine)
- app/worker.py (ensure Celery is configured for production)
- tests/test_retry.py (update)
  Dependencies / Required Vars:
- CELERY_BROKER_URL, CELERY_RESULT_BACKEND, REDIS_URL
  Acceptance Criteria ✅:
- ✅ Retry engine schedules attempts via Celery and respects policy rules.
- ✅ Idempotency enforced for retries (prevents duplicate charges).
- ✅ Tests simulate policy-driven retries and pass.
  CLI Commands:
- git checkout -b feature/retry-engine
- git commit -m "feat(retry): add retry engine scaffold and Celery wiring"

---

Module 10 — PSP Adapter Interface
Goal: Create a unified adapter interface for Stripe & Razorpay (operations: create_payment, capture, refund, webhook verification).
Files:

- app/psp/psp_adapter.py (new)
- app/psp/stripe_adapter.py (edit to implement interface)
- app/psp/razorpay_adapter.py (edit to implement interface)
- tests/test_psp_adapters.py (new)
  Dependencies / Required Vars:
- STRIPE_SECRET_KEY, RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
  Acceptance Criteria ✅:
- ✅ Adapters expose unified methods and are mocked in tests.
- ✅ Webhook signature verification helpers present.
  CLI Commands:
- git checkout -b feature/psp-adapter
- git commit -m "feat(psp): add adapter interface and wire Stripe/Razorpay"

---

Module 11 — Reconciliation Job
Goal: Periodic job to compare PSP transactions vs internal transactions and flag mismatches.
Files:

- app/tasks/reconciliation.py (new)
- app/services/reconciliation_service.py (new)
- tests/test_reconciliation.py (new)
  Dependencies / Required Vars:
- RECONCILIATION_WINDOW_DAYS, PSP_API_KEYS
  Acceptance Criteria ✅:
- ✅ Reconciliation run produces a reconcile report and stores mismatches.
- ✅ Reconciliation job schedulable via Celery beat.
  CLI Commands:
- git checkout -b feature/reconciliation
- git commit -m "feat(reconcile): add reconciliation task + report"

---

Module 12 — Notification Service
Goal: Email/SMS reminders using SMTP/Twilio with template rendering and retry on failure.
Files:

- app/services/notifications/email_service.py (new)
- app/services/notifications/sms_service.py (new)
- app/services/template_renderer.py (new)
- app/templates/email/base.html (new)
- app/templates/email/recovery_link.html (new)
- tests/test_notifications.py (new)
  Dependencies / Required Vars:
- SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_PHONE
  Acceptance Criteria ✅:
- ✅ Sending email and SMS works in staging with test keys.
- ✅ Template variables substituted correctly; preview endpoint available.
  CLI Commands:
- git checkout -b feature/notifications
- git commit -m "feat(notifications): add SMTP/Twilio services and templates"

---

Module 13 — Audit Logs Service
Goal: Track admin/user actions in a tamper-evident audit log (append-only, searchable).
Files:

- app/services/audit_logs.py (new)
- app/models.py (edit - AuditLog model)
- app/routers/audit.py (new - minimal read-only access for admins)
  Dependencies / Required Vars:
- AUDIT_DB_URL (optional: separate store)
  Acceptance Criteria ✅:
- ✅ Actions (create/update/delete) recorded with user_id, org_id, timestamp, ip, request_id.
- ✅ Admins can query logs via API (read-only), logs immutable by API.
  CLI Commands:
- git checkout -b feature/audit-logs
- git commit -m "feat(audit): add audit logs service and API"

---

Module 14 — Partition Pruning Task
Goal: Monthly Postgres partition cleanup and archival to S3 (or drop after retention window).
Files:

- app/tasks/partition_prune.py (new)
- app/services/partition_manager.py (new)
- tests/test_partition_prune.py (new)
  Dependencies / Required Vars:
- DATABASE_URL, S3_BUCKET, S3_ACCESS_KEY, S3_SECRET_KEY, PARTITION_RETENTION_DAYS
  Acceptance Criteria ✅:
- ✅ Task moves older partitions to S3 (if configured) and removes old partitions per retention policy.
- ✅ Dry-run mode available for safety.
  CLI Commands:
- git checkout -b feature/partition-prune
- git commit -m "feat(partition): add monthly pruning task + dry-run"

---

Module 15 — Analytics Sink
Goal: Stream analytics data to ClickHouse or S3 for long-term storage and BI.
Files:

- app/services/analytics_sink.py (new)
- app/routers/analytics.py (edit to produce events)
- infra/ (k8s/helm) and docs for sink configuration
  Dependencies / Required Vars:
- CLICKHOUSE_URL (optional), S3_ACCESS_KEY, S3_SECRET_KEY, ANALYTICS_SINK_TYPE
  Acceptance Criteria ✅:
- ✅ Events stream into sink in bulk or streaming mode.
- ✅ Historical queries possible in BI (ClickHouse) using sample data.
  CLI Commands:
- git checkout -b feature/analytics-sink
- git commit -m "feat(analytics): add clickhouse/s3 sink scaffold"

---

Module 16 — CI/CD Pipeline
Goal: Build + test + deploy via GitHub Actions (staging + production), image pushes and promotion.
Files:

- .github/workflows/ci.yml (edit - add matrix, caching)
- .github/workflows/deploy.yml (new - staging deploy)
- Dockerfile (verify multi-stage) (edit)
- infra/scripts/deploy.sh (new)
  Dependencies / Required Vars:
- GITHUB_TOKEN, DOCKER_REGISTRY, K8S_CLUSTER_CREDENTIALS, CLOUD_PROVIDER_SECRETS
  Acceptance Criteria ✅:
- ✅ PRs run tests and lint in CI, build images and push to registry on merge to main.
- ✅ Deploy to staging on merge to staging branch.
  CLI Commands:
- git checkout -b ci/cd-pipeline
- git commit -m "ci: add deploy workflow and improve ci caching"

---

Module 17 — Managed Postgres Migration
Goal: Ensure cloud DB connection setup, migrations via Alembic, and secure secrets in CI.
Files:

- alembic.ini (edit - set env variables), migrations/env.py (edit)
- infra/README-db.md (new)
  Dependencies / Required Vars:
- DATABASE_URL (production), DATABASE_READONLY_URL (optional)
  Acceptance Criteria ✅:
- ✅ Alembic runs migrations against managed DB in staging and production.
- ✅ Secrets stored in GitHub or Cloud provider secret manager (not in repo).
  CLI Commands:
- git checkout -b infra/managed-postgres
- git commit -m "chore(db): add instructions and secure migration steps"

---

Module 18 — Autoscaling & Monitoring
Goal: HPA YAML, Prometheus metrics endpoint and Grafana dashboards; Sentry wired to both backend & frontend.
Files:

- k8s/hpa.yml (edit), k8s/metrics-service.yml (new)
- app/metrics.py (new - prometheus instrumentation)
- tinko-console/lib/sentry.ts (edit - frontend Sentry)
  Dependencies / Required Vars:
- PROMETHEUS_URL, GRAFANA_API_KEY, SENTRY_DSN
  Acceptance Criteria ✅:
- ✅ /metrics endpoint available and scraped by Prometheus.
- ✅ HPA autoscaling configured for CPU/memory and custom metrics.
- ✅ Sentry reports visible for backend and frontend errors.
  CLI Commands:
- git checkout -b infra/monitoring
- git commit -m "chore(monitoring): add prometheus instrumentation and hpa manifests"

---

Module 19 — Rate Limiting & Security
Goal: Add slowapi rate limiting, JWT rotation, idempotency keys and password rules.
Files:

- app/middleware/rate_limit.py (new)
- app/security.py (edit - JWT rotation, password policy)
- app/middleware/idempotency.py (new)
- tests/test_rate_limit.py (new)
  Dependencies / Required Vars:
- RATE_LIMIT_RULES, JWT_SECRET, IDP_CONFIG (for SSO)
  Acceptance Criteria ✅:
- ✅ Rate limiting enforced on auth endpoints.
- ✅ Idempotency keys supported for payment creation endpoints.
- ✅ Password strength validation and reset flows present.
  CLI Commands:
- git checkout -b feature/security-rate-limits
- git commit -m "feat(security): add rate limiting and idempotency middleware"

---

## Section 4: File Tree Scaffold (expected final structure)

app/

- main.py
- db.py
- models.py
- services/
  - classifier.py
  - retry_engine.py
  - template_renderer.py
  - analytics_sink.py
  - audit_logs.py
- psp/
  - psp_adapter.py
  - stripe_adapter.py
  - razorpay_adapter.py
- routers/
  - auth.py
  - rules.py
  - analytics.py
  - payments.py
  - webhooks_stripe.py
  - webhooks_razorpay.py
    tasks/
- reconciliation.py
- partition_prune.py
  tinko-console/
- app/
  - (console)/
    - dashboard/
    - rules/
    - settings/
    - onboarding/
  - components/
    - charts/
    - rules/rule-builder.tsx

---

## Section 5: Environment Variables

| Category      |                   Key | Purpose                  | Example                                |
| ------------- | --------------------: | ------------------------ | -------------------------------------- |
| Core          |          DATABASE_URL | DB connection            | postgresql://user:pass@localhost/tinko |
| Core          |             REDIS_URL | Celery broker/cache      | redis://localhost:6379/0               |
| Auth          |       NEXTAUTH_SECRET | NextAuth / SSO secret    | devnextsecret123                       |
| Auth          |            JWT_SECRET | JWT signing key          | jwtsecret123                           |
| PSP           |     STRIPE_SECRET_KEY | Stripe secret            | sk_test_xxx                            |
| PSP           | STRIPE_WEBHOOK_SECRET | Stripe webhook signature | whsec_xxx                              |
| PSP           |       RAZORPAY_KEY_ID | Razorpay key id          | rzp_test_xxx                           |
| PSP           |   RAZORPAY_KEY_SECRET | Razorpay key secret      | rzsecret_xxx                           |
| Queue         |     CELERY_BROKER_URL | Celery broker            | redis://localhost:6379/0               |
| Queue         | CELERY_RESULT_BACKEND | Celery result backend    | redis://localhost:6379/1               |
| Notifications |             SMTP_HOST | SMTP server              | smtp.sendgrid.net                      |
| Notifications |             SMTP_PORT | SMTP port                | 587                                    |
| Notifications |             SMTP_USER | SMTP user                | no-reply@tinko.in                      |
| Notifications |             SMTP_PASS | SMTP password            | <placeholder>                          |
| Notifications |    TWILIO_ACCOUNT_SID | Twilio SID               | ACxxxxxxxxxxxxxxxx                     |
| Notifications |     TWILIO_AUTH_TOKEN | Twilio Auth              | yourtokenhere                          |
| Analytics     |        CLICKHOUSE_URL | ClickHouse DSN           | http://clickhouse:8123                 |
| Analytics     |         S3_ACCESS_KEY | S3 access key            | AKIA...                                |
| Infra         |            SENTRY_DSN | Sentry DSN               | https://dsn@sentry.io/123              |
| Frontend      |   NEXT_PUBLIC_API_URL | API base URL             | https://api.tinko.in                   |

Notes:

- Never commit real secrets to git. Use .env (local) and secret manager in CI/CD.

---

## Section 6: Build Commands & Automation (bash)

High-level commands you'll use repeatedly (example flows):

Initialize local env & start services

```bash
# Create branch
git checkout -b phase1-frontend

# Install backend deps
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start local Postgres + Redis via docker-compose
docker compose up -d postgres redis

# Start backend (dev)
cd Stealth-Reecovery
uvicorn app.main:app --reload

# Start frontend (dev)
cd tinko-console
npm install
npm run dev

# Run tests
pytest -v

# Start Celery worker (Windows note: --pool=solo)
celery -A app.worker worker --loglevel=info --pool=solo
celery -A app.worker beat --loglevel=info
```

CI / PR / Deploy sample steps

```bash
# On feature branch after changes
git add -A
git commit -m "feat(module): short summary"
git push origin feature/your-branch

# Open PR; CI will run tests and lint

# On merge to main, GitHub Actions builds images and deploys to staging (if configured)
```

Recommended git commit template (copy into terminal when committing):

```bash
git commit -m "<type>(<scope>): <short summary>\n\n<detailed description>\n\nRefs: #<issue-number>"
```

---

## Section 7: Final Checklist (go/no-go)

- [ ] Frontend modules complete (1–4)
- [ ] Customer Payer flows functional (5–7)
- [ ] Backend core implemented (8–13)
- [ ] Notifications working and tested
- [ ] Celery and Redis running in staging
- [ ] Reconciliation and partition pruning scheduled
- [ ] CI/CD pipelines build and deploy staging
- [ ] Prometheus + Grafana + Sentry wired
- [ ] Tests >= 95% passing on CI
- [ ] Docker images built and pushed

---

## Appendix: Small CLI helpers (examples)

Create feature branch and scaffold commit

```bash
feature="classifier"
git checkout -b feature/$feature
mkdir -p app/services
echo "# TODO: implement" > app/services/${feature}.py
git add app/services/${feature}.py
git commit -m "chore(scaffold): add ${feature} service stub"
```

Deploy to staging (example script placeholder)

```bash
# infra/scripts/deploy-staging.sh
echo "Building images..."
docker build -t $DOCKER_REGISTRY/tinko-backend:staging -f Dockerfile .
docker push $DOCKER_REGISTRY/tinko-backend:staging
# Trigger k8s rollout or cloud deploy here
```

---

Completion summary

- What changed: This file is the authoritative single-file build plan; it lists all modules, files to change, env variables, acceptance criteria and CLI commands required to move the project from current state to production-ready.
- How this was verified: Plan created from repository audit docs (PROJECT_STATUS_SUMMARY.md, ACTIONABLE_TASKS.md, outstanding_work.json) and by scanning `app/` + `tinko-console/` structure.

Next steps (recommended immediate):

1. Configure Redis + Celery locally and run tests (see audit docs for commands).
2. Implement Notifications (email + sms) and run end-to-end retry test.
3. Implement RBAC and Razorpay adapter.

---

END OF FULL_BUILD_PLAN.md
