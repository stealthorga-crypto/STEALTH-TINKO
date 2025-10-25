"# Tinko - Stealth Recovery Platform

> **Failed Payment Recovery System with AI-Powered Classification**

[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)](.)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen)](.)
[![Docs](https://img.shields.io/badge/Docs-Consolidated-blue)](./CONSOLIDATED_DOCUMENTATION.md)

## 🚀 Quick Links

- **📚 [Complete Documentation](./CONSOLIDATED_DOCUMENTATION.md)** - All project documentation in one place (342KB)
- **🎯 [Quick Start - PSP-001](./CONSOLIDATED_DOCUMENTATION.md#psp-001-quick-start)** - Payment service provider integration
- **🔄 [Quick Start - Retry](./CONSOLIDATED_DOCUMENTATION.md#retry-quick-start)** - Retry mechanism setup
- **📦 [Archive](./CONSOLIDATION_SUMMARY.md)** - Documentation consolidation details

## 📖 About

Tinko is a comprehensive failed payment recovery platform that helps businesses recover lost revenue through:

- **Automated Payment Recovery** - Smart retry mechanisms
- **Stripe Integration** - PSP-001 payment service provider
- **AI Classification** - Intelligent failure analysis
- **Analytics Dashboard** - Real-time metrics and insights
- **Scalable Architecture** - Partition strategy for high volume

## 🏗️ Project Structure

```
Stealth-Reecovery/
├── app/                          # Backend (FastAPI)
│   ├── routers/                  # API routes
│   ├── services/                 # Business logic
│   ├── psp/                      # Payment service providers
│   └── models.py                 # Database models
├── tinko-console/                # Frontend (Next.js)
│   ├── app/                      # App router pages
│   ├── components/               # React components
│   └── lib/                      # Utilities
├── tests/                        # Test suite
├── docs/                         # Additional documentation
└── CONSOLIDATED_DOCUMENTATION.md # Master documentation (START HERE)
```

## 🎯 Quick Start

1. **Read the Documentation**

   ```bash
   # Open consolidated docs
   code CONSOLIDATED_DOCUMENTATION.md
   ```

2. **Backend Setup**

   ```bash
   # From the repository root (preferred)
   pip install -r requirements.txt
   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8010

   # If port 8010 is busy, pick any free port and set NEXT_PUBLIC_API_URL accordingly
   ```

3. **Frontend Setup**

   ```bash
   cd tinko-console
   npm install
   # Ensure the console points to the API base URL
   # (create .env.local and set NEXT_PUBLIC_API_URL if needed)
   # NEXT_PUBLIC_API_URL=http://127.0.0.1:8010
   npm run dev
   ```

4. **See Full Instructions**
   - [Deployment Guide](./CONSOLIDATED_DOCUMENTATION.md#deployment--operations)
   - [Docker Guide](./CONSOLIDATED_DOCUMENTATION.md#docker-guide)
   - [Testing Guide](./CONSOLIDATED_DOCUMENTATION.md#testing--quality)

### Razorpay Payer Flow (dev)

- Backend creates orders at `POST /v1/payments/razorpay/orders-public` with `{ ref }` and serves a webhook at `POST /v1/payments/razorpay/webhooks`.
- Frontend payer routes:
  - `/pay/[ref]/checkout` (direct by transaction ref)
  - `/pay/retry/[token]/checkout` (token-based flow resolving ref)
  - `/pay/retry/[token]` (optional schedule picker → checkout)
- Env:
  - `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET` (server)
  - `NEXT_PUBLIC_API_URL=http://127.0.0.1:8010` (frontend)

#### cURL snippets

```bash
# Persist a selected schedule (use token as Bearer)
curl -X PATCH "$NEXT_PUBLIC_API_URL/v1/recoveries/123/next_retry_at" \
   -H "Authorization: Bearer $TOKEN_FROM_LINK" \
   -H 'Content-Type: application/json' \
   -d '{"next_retry_at":"2025-10-24T10:00:00Z"}'

# Trigger due retries using in-process fallback (admin JWT)
curl -X POST "$NEXT_PUBLIC_API_URL/v1/retry/trigger-due" \
   -H "Authorization: Bearer $ADMIN_JWT"

# Razorpay webhook (replace BODY and signature accordingly)
curl -X POST "$NEXT_PUBLIC_API_URL/v1/payments/razorpay/webhooks" \
   -H "X-Razorpay-Signature: $SIG_HEX" \
   -H 'Content-Type: application/json' \
   -d @payload.json
```

### Partitions & Maintenance

- Ensure partitions (Postgres only, no-op on SQLite): `POST /v1/maintenance/partition/ensure_current` (admin only)
- Migration `005_partitions.py` attempts to create and attach monthly partitions for `transactions_*`.

### Analytics Sink (optional)

Toggle sinks with flags:

```
FEATURE_ANALYTICS_SINK=on
FEATURE_CLICKHOUSE_SINK=off
FEATURE_S3_SINK=off
```

Supported envs: `CLICKHOUSE_URL`, `CLICKHOUSE_DATABASE`, `CLICKHOUSE_TABLE`, `S3_BUCKET_NAME`, `S3_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`.

### i18n

Minimal dictionaries exist for English, Tamil, and Hindi. Use the language switcher in the console header.

### Dev Note: Duplicate app folder

This repo contains a historical nested copy under `Stealth-Reecovery/`. Always run from the repository root (`app/…`). Newer endpoints (Razorpay, schedule persist, retry fallback, maintenance) exist only in the root app.

### Stripe Webhook (development)

To receive Stripe events locally, use the Stripe CLI to forward webhooks to the API. Ensure `STRIPE_WEBHOOK_SECRET` is set from the CLI output.

Example:

1. Start a listener:

   stripe listen --forward-to http://localhost:8000/v1/webhooks/stripe

2. Copy the `whsec_...` secret from the CLI output into your `.env` as `STRIPE_WEBHOOK_SECRET` and restart the API.

Optionally restrict to specific events with `--events payment_intent.succeeded,payment_intent.payment_failed`

## 📊 Current Status

✅ **Backend:** Production ready with Stripe integration  
✅ **Frontend:** Next.js dashboard with analytics  
✅ **Tests:** 100% pass rate (43/43 tests)  
✅ **Documentation:** Consolidated and organized  
✅ **CI/CD:** Automated deployment workflows

## 📚 Documentation

All documentation has been consolidated into a single comprehensive file:

**[📖 CONSOLIDATED_DOCUMENTATION.md](./CONSOLIDATED_DOCUMENTATION.md)** - 342KB containing:

1. Project Overview
2. Quick Start Guides
3. Implementation Status
4. Architecture & Design
5. Deployment & Operations
6. Testing & Quality
7. Frontend (Tinko Console)
8. Specifications
9. Changelog & Reports

### Why Consolidated?

- ✅ Single source of truth
- ✅ Easy to search and navigate
- ✅ Consistent formatting
- ✅ Better maintenance
- ✅ Reduced clutter (44 files → 1 file)

## 🛠️ Technology Stack

**Backend:**

- FastAPI (Python)
- SQLAlchemy ORM
- Stripe SDK
- PostgreSQL/SQLite

**Frontend:**

- Next.js 15
- React 19
- Tailwind CSS
- TypeScript

**Infrastructure:**

- Docker
- GitHub Actions
- Vercel (Frontend)

## 🤝 Contributing

See [CONSOLIDATED_DOCUMENTATION.md](./CONSOLIDATED_DOCUMENTATION.md) for complete development guidelines.

## 📝 License

See LICENSE file for details.

## 📧 Support

For questions or issues, please refer to the [consolidated documentation](./CONSOLIDATED_DOCUMENTATION.md) first.

---

**Last Updated:** October 20, 2025  
**Repository:** stealthorga-crypto/STEALTH-TINKO  
**Documentation Status:** ✅ Consolidated"
