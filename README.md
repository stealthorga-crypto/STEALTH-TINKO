# 🚀 STEALTH-TINKO Recovery Platform

[![CI Status](https://github.com/stealthorga-crypto/STEALTH-TINKO/actions/workflows/ci.yml/badge.svg)](https://github.com/stealthorga-crypto/STEALTH-TINKO/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**STEALTH-TINKO** is an intelligent payment failure recovery platform that helps merchants automatically retry failed transactions and recover lost revenue through smart recovery workflows.

## 📊 Project Status

🚧 **DEVELOPMENT** - Core features working, NOT production-ready yet

- ✅ **31% Production Ready** (25/80 score)
- ✅ Core payment recovery flow working
- ⚠️ Missing: Real authentication, automated retry engine, production infrastructure
- 📅 **Estimated MVP**: 10-12 weeks from now

See [APPLICATION_HEALTH_STATUS.txt](./APPLICATION_HEALTH_STATUS.txt) for detailed status.

## ✨ Features

### ✅ Currently Working
- Payment failure event ingestion via REST API
- Automatic failure classification (6 categories)
- Secure recovery link generation with expiring tokens
- Customer-facing recovery pages
- Stripe payment integration with webhook handling
- Database models and migrations (Alembic)
- Frontend dashboard (Next.js) with all UI pages

### 🚧 In Development
- Real authentication & RBAC
- Automated retry scheduling (Celery)
- Email/SMS notifications
- Database-driven rules engine
- Real-time analytics
- Multi-tenancy support

## 🏗️ Architecture

```
STEALTH-TINKO/
├── app/                    # FastAPI backend
│   ├── analytics/          # Analytics modules
│   ├── config/             # Configuration
│   ├── psp/               # Payment Service Provider integrations
│   ├── routers/           # API endpoints
│   ├── services/          # Business logic
│   └── tasks/             # Background tasks
├── tinko-console/         # Next.js frontend
├── db/                    # Database schemas
├── migrations/            # Alembic migrations
├── tests/                 # Test suite
└── docker-compose.yml     # Local development setup
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (or use Docker)
- Redis (for background tasks)

### 1. Clone the Repository
```bash
git clone https://github.com/stealthorga-crypto/STEALTH-TINKO.git
cd STEALTH-TINKO
```

### 2. Set Up Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required environment variables:**
- `DATABASE_URL` - PostgreSQL connection string
- `STRIPE_SECRET_KEY` - Stripe API key
- `STRIPE_WEBHOOK_SECRET` - Stripe webhook secret
- `JWT_SECRET` - Secret for JWT tokens (32+ characters)

### 3. Run with Docker (Recommended)
```bash
# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Access services
# - Backend API: http://localhost:8000
# - Frontend: http://localhost:3000
# - MailHog UI: http://localhost:8025
```

### 4. Manual Setup (Development)

**Backend:**
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd tinko-console
npm install
npm run dev
```

## 📖 API Documentation

Once running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints
```
POST   /v1/events              # Ingest payment failure
POST   /v1/recovery-links      # Generate recovery link
GET    /v1/token/validate      # Validate recovery token
POST   /webhooks/stripe        # Stripe webhook handler
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_classifier.py
```

## 🔒 Security

### ⚠️ IMPORTANT - Exposed Secrets Alert

This repository has **2 exposed Stripe webhook secrets** in git history. If you're maintaining this project:

1. **Immediately rotate** the exposed keys in Stripe Dashboard
2. **Never commit** real secrets to git
3. Always use `.env` files (already in `.gitignore`)
4. Use environment variables for all sensitive data

See [SECURITY.md](./SECURITY.md) for full security guidelines.

## 📋 Roadmap

### Phase 1: Security & Foundation (Weeks 1-4)
- [ ] Implement real authentication (JWT + OAuth)
- [ ] Add rate limiting and CSRF protection
- [ ] Set up Sentry error tracking
- [ ] Create Docker production images

### Phase 2: Automation (Weeks 5-8)
- [ ] Build Celery retry engine
- [ ] Implement email/SMS notifications
- [ ] Add database-driven rules engine
- [ ] Connect frontend to real analytics APIs

### Phase 3: Production Ready (Weeks 9-12)
- [ ] Multi-tenancy with org isolation
- [ ] Production deployment pipeline
- [ ] Monitoring & observability
- [ ] End-to-end testing suite

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md) first.

### Development Workflow
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see [LICENSE](./LICENSE) file for details.

## 👥 Contributors

- [@meruem89](https://github.com/meruem89) - Project Lead
- [@sadishsugumaran](https://github.com/sadishsugumaran) - Core Developer

## 📞 Support

- 📧 Email: info@blocksandloops.com
- 🐛 Issues: [GitHub Issues](https://github.com/stealthorga-crypto/STEALTH-TINKO/issues)
- 📖 Docs: [Full Documentation](./CONSOLIDATED_DOCUMENTATION.md)

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Frontend powered by [Next.js](https://nextjs.org/)
- Payment processing via [Stripe](https://stripe.com/)

---

**⚡ Built with ❤️ by the STEALTH-TINKO Team**
