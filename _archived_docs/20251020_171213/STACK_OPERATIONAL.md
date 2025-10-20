# Tinko Recovery Stack - Quick Reference

**Session:** 20251018-173230  
**Status:** ✅ ALL SERVICES OPERATIONAL

## Services Running (7/7)

```
✅ backend   - http://localhost:8000 - API Server
✅ frontend  - http://localhost:3000 - Next.js UI
✅ db        - postgresql://localhost:5432 - PostgreSQL 15
✅ redis     - redis://localhost:6379 - Redis 7
✅ mailhog   - http://localhost:8025 - Email UI (SMTP: 1025)
✅ worker    - Celery worker (background tasks)
✅ beat      - Celery beat (scheduler)
```

## Health Checks

```bash
# Backend API
curl http://localhost:8000/healthz
# Expected: {"ok":true}

# Frontend UI
curl -I http://localhost:3000
# Expected: HTTP/1.1 200 OK

# Service Status
docker compose ps
# Expected: All services "Up" or "Healthy"
```

## Common Commands

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f backend
docker compose logs -f worker
docker compose logs -f beat

# Restart specific service
docker compose restart backend

# Rebuild and restart
docker compose build backend
docker compose up -d backend worker beat

# Access backend shell
docker compose exec backend sh

# Run database migrations
docker compose exec backend alembic upgrade head

# Check worker status
docker compose exec worker celery -A app.worker:celery_app inspect active
```

## API Endpoints

- `/healthz` - Health check
- `/docs` - Swagger UI (interactive API docs)
- `/openapi.json` - OpenAPI schema
- `/v1/classify` - Classify payment failure
- `/v1/events/*` - Event tracking
- `/v1/payments/stripe/*` - Stripe payment operations
- `/v1/recoveries/*` - Recovery management
- `/v1/retry/*` - Retry policy management
- `/v1/webhooks/stripe` - Stripe webhook handler

## Stripe Webhook Setup

```bash
# 1. Install Stripe CLI (if not already installed)
# Windows: scoop install stripe
# Mac: brew install stripe/stripe-cli/stripe

# 2. Login to Stripe
stripe login

# 3. Start webhook listener
bash scripts/stripe_listen.sh

# 4. Copy webhook signing secret from CLI output
# 5. Add to .env file:
#    STRIPE_WEBHOOK_SECRET=whsec_...

# 6. Restart backend
docker compose restart backend
```

## Troubleshooting

### Worker/Beat Not Running

```bash
# Check logs for errors
docker compose logs worker --tail=50
docker compose logs beat --tail=50

# Restart worker and beat
docker compose restart worker beat

# If still failing, check Redis connection
docker compose exec worker redis-cli -h redis ping
```

### Backend Connection Refused

```bash
# Check if backend is running
docker compose ps backend

# Check backend logs
docker compose logs backend --tail=100

# Restart backend
docker compose restart backend

# If database issue, check migrations
docker compose exec backend alembic current
docker compose exec backend alembic upgrade head
```

### Frontend Build Errors

```bash
# Rebuild frontend
docker compose build frontend

# Check frontend logs
docker compose logs frontend --tail=100

# If port conflict, check what's using port 3000
# Windows: netstat -ano | findstr :3000
# Kill process: taskkill /PID <pid> /F
```

## Next Steps

1. ⚠️ Implement RULES-001 endpoints (`/v1/rules/*`)
2. ⚠️ Implement TMPL-001 endpoints (`/v1/templates/*`)
3. 🔧 Set up Stripe CLI webhook forwarding
4. 🧪 Run pytest suite (after fixing test containerization)
5. 🧪 Run end-to-end smoke test

## Logs

All operations logged to: `_logs/20251018-173230/`

## Full Report

See: `_logs/20251018-173230/DELIVERY_REPORT.md`
