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
   cd Stealth-Reecovery
   pip install -r requirements.txt
   python -m uvicorn app.main:app --reload
   ```

3. **Frontend Setup**

   ```bash
   cd tinko-console
   npm install
   npm run dev
   ```

4. **See Full Instructions**
   - [Deployment Guide](./CONSOLIDATED_DOCUMENTATION.md#deployment--operations)
   - [Docker Guide](./CONSOLIDATED_DOCUMENTATION.md#docker-guide)
   - [Testing Guide](./CONSOLIDATED_DOCUMENTATION.md#testing--quality)

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
