#!/usr/bin/env bash
# Tinko Recovery - Complete Setup Script
# Run from repository root: bash NEXT_STEPS.sh

set -euo pipefail

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  TINKO RECOVERY - Production Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 0) Create env templates (safe to commit)
echo "📝 Step 0: Creating environment templates..."
cat > .env.example <<'ENV'
# ============================================================================
# TINKO RECOVERY - BACKEND ENVIRONMENT VARIABLES
# ============================================================================
# Copy to .env and fill with real values (DO NOT COMMIT .env)

# Database
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/tinko

# API Configuration
PUBLIC_BASE_URL=http://localhost:8000

# Authentication & Security
JWT_SECRET=replace_with_secure_random_string_min_32_chars
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=1440

# Stripe Payment Gateway
STRIPE_SECRET_KEY=sk_test_replace_with_your_stripe_secret
STRIPE_WEBHOOK_SECRET=whsec_replace_with_your_webhook_secret

# Redis (for Celery task queue)
REDIS_URL=redis://redis:6379/0

# Email (SMTP)
SMTP_HOST=mailhog
SMTP_PORT=1025
SMTP_USER=
SMTP_PASS=

# SMS (Twilio)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM_PHONE=

# Observability
SENTRY_DSN=
LOG_LEVEL=INFO

# Additional Payment Service Providers (fill when enabling)
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
RAZORPAY_WEBHOOK_SECRET=
PAYU_MERCHANT_ID=
PAYU_MERCHANT_KEY=
CASHFREE_APP_ID=
CASHFREE_SECRET_KEY=
ENV

mkdir -p tinko-console
cat > tinko-console/.env.example <<'ENV'
# ============================================================================
# TINKO RECOVERY - FRONTEND ENVIRONMENT VARIABLES
# ============================================================================
# Copy to .env.local and fill with real values (DO NOT COMMIT .env.local)

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=replace_with_secure_random_string_min_32_chars

# Feature Flags
NEXT_PUBLIC_PAYMENTS_DEMO=true

# Observability
NEXT_PUBLIC_SENTRY_DSN=
ENV

echo "✅ Environment templates created"

# 1) Dockerize stack
echo ""
echo "🐳 Step 1: Creating Docker configuration..."
cat > Dockerfile <<'DOCKER'
FROM python:3.11-slim AS base

WORKDIR /app

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run database migrations on startup, then start server
CMD alembic upgrade head && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000
DOCKER

cat > tinko-console/Dockerfile <<'DOCKER'
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --legacy-peer-deps

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
ENV PORT=3000
CMD ["node", "server.js"]
DOCKER

cat > docker-compose.yml <<'YML'
version: "3.9"

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: tinko
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  mailhog:
    image: mailhog/mailhog
    ports:
      - "1025:1025"  # SMTP
      - "8025:8025"  # Web UI

  backend:
    build: .
    env_file: .env
    environment:
      DATABASE_URL: postgresql+psycopg2://postgres:postgres@db:5432/tinko
      REDIS_URL: redis://redis:6379/0
      SMTP_HOST: mailhog
      SMTP_PORT: 1025
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app/app
      - ./migrations:/app/migrations
      - ./alembic.ini:/app/alembic.ini
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3

  worker:
    build: .
    env_file: .env
    command: celery -A app.worker.celery worker -l info
    environment:
      DATABASE_URL: postgresql+psycopg2://postgres:postgres@db:5432/tinko
      REDIS_URL: redis://redis:6379/0
      SMTP_HOST: mailhog
      SMTP_PORT: 1025
    depends_on:
      - db
      - redis
      - backend
    volumes:
      - ./app:/app/app

  frontend:
    build: ./tinko-console
    env_file: ./tinko-console/.env.local
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
      NEXTAUTH_URL: http://localhost:3000
    depends_on:
      - backend
    ports:
      - "3000:3000"

volumes:
  postgres_data:
  redis_data:
YML

echo "✅ Docker configuration created"

# 2) Local envs (do NOT commit .env files)
echo ""
echo "🔐 Step 2: Creating local environment files..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env (FILL WITH REAL VALUES)"
else
    echo "⚠️  .env already exists, skipping"
fi

if [ ! -f tinko-console/.env.local ]; then
    cp tinko-console/.env.example tinko-console/.env.local
    echo "✅ Created tinko-console/.env.local (FILL WITH REAL VALUES)"
else
    echo "⚠️  tinko-console/.env.local already exists, skipping"
fi

# 3) Bring the stack up
echo ""
echo "🚀 Step 3: Starting Docker containers..."
docker compose up -d --build

echo "⏳ Waiting for database to be ready..."
sleep 10

# 4) Run Alembic migrations
echo ""
echo "📊 Step 4: Running database migrations..."
docker compose exec -T backend bash -c 'alembic upgrade head' || echo "⚠️  Migration failed or alembic not configured"

# 5) Smoke tests
echo ""
echo "🧪 Step 5: Running smoke tests..."
echo "Backend tests:"
docker compose exec -T backend bash -c 'pytest -q --disable-warnings' || echo "⚠️  Some tests failed"

echo ""
echo "Health check:"
curl -sS http://localhost:8000/healthz && echo " ✅" || echo "❌ Backend not responding"

# 6) Install auth dependencies
echo ""
echo "🔒 Step 6: Setting up authentication scaffolding..."
docker compose exec -T backend bash -c 'pip install passlib[bcrypt] python-jose[cryptography]'

# Create app/security.py
docker compose exec -T backend bash -c "cat > app/security.py <<'PY'
\"\"\"
Authentication and security utilities for JWT and password hashing.
\"\"\"
from datetime import datetime, timedelta
from typing import Dict, Any
from jose import jwt
from passlib.context import CryptContext
import os

# Password hashing context
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(password: str) -> str:
    \"\"\"Hash a plain password using bcrypt.\"\"\"
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    \"\"\"Verify a plain password against a hashed password.\"\"\"
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt(
    data: Dict[str, Any],
    secret: str = None,
    minutes: int = None,
    algorithm: str = None
) -> str:
    \"\"\"
    Create a JWT token with the given data.
    
    Args:
        data: Dictionary to encode in the token
        secret: JWT secret (defaults to env var JWT_SECRET)
        minutes: Token expiry in minutes (defaults to env var JWT_EXPIRY_MINUTES)
        algorithm: JWT algorithm (defaults to env var JWT_ALGORITHM)
    \"\"\"
    secret = secret or os.getenv('JWT_SECRET', 'dev-secret-change-in-production')
    minutes = minutes or int(os.getenv('JWT_EXPIRY_MINUTES', '1440'))
    algorithm = algorithm or os.getenv('JWT_ALGORITHM', 'HS256')
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=minutes)
    to_encode['exp'] = expire
    
    return jwt.encode(to_encode, secret, algorithm=algorithm)


def decode_jwt(token: str, secret: str = None, algorithm: str = None) -> Dict[str, Any]:
    \"\"\"
    Decode and verify a JWT token.
    
    Args:
        token: JWT token string
        secret: JWT secret (defaults to env var JWT_SECRET)
        algorithm: JWT algorithm (defaults to env var JWT_ALGORITHM)
    \"\"\"
    secret = secret or os.getenv('JWT_SECRET', 'dev-secret-change-in-production')
    algorithm = algorithm or os.getenv('JWT_ALGORITHM', 'HS256')
    
    return jwt.decode(token, secret, algorithms=[algorithm])
PY
"

echo "✅ Created app/security.py"

# 7) Install Celery dependencies
echo ""
echo "⚙️  Step 7: Setting up Celery worker scaffolding..."
docker compose exec -T backend bash -c 'pip install celery==5.3.4 redis==5.0.1'

docker compose exec -T backend bash -c "cat > app/worker.py <<'PY'
\"\"\"
Celery worker configuration for async task processing.
\"\"\"
from celery import Celery
import os

# Initialize Celery app
celery = Celery(
    'tinko',
    broker=os.getenv('REDIS_URL', 'redis://redis:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://redis:6379/0')
)

# Configure Celery
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)


@celery.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3}
)
def ping(self):
    \"\"\"Test task to verify Celery is working.\"\"\"
    return 'pong'


# Import task modules here when created
# from app.tasks import retry_tasks
PY
"

echo "✅ Created app/worker.py"

# 8) Restart services to pick up new code
echo ""
echo "🔄 Step 8: Restarting services..."
docker compose restart backend worker

# 9) Open UIs
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ SETUP COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Access your services:"
echo "   Backend API:  http://localhost:8000"
echo "   API Docs:     http://localhost:8000/redoc"
echo "   Frontend:     http://localhost:3000"
echo "   Mailhog:      http://localhost:8025"
echo ""
echo "📋 Next steps:"
echo "   1. Edit .env and tinko-console/.env.local with real values"
echo "   2. Restart services: docker compose restart"
echo "   3. Test auth flow: Implement AUTH-001"
echo "   4. Verify worker: docker compose exec worker celery -A app.worker.celery inspect ping"
echo ""
echo "📚 Task tracking:"
echo "   - outstanding_work.json (11 tasks, 4 phases)"
echo "   - issues.yml (14 security/reliability issues)"
echo ""
echo "🔧 Development commands:"
echo "   View logs:     docker compose logs -f backend"
echo "   Run tests:     docker compose exec backend pytest"
echo "   Shell access:  docker compose exec backend bash"
echo "   Stop all:      docker compose down"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 10) Commit scaffolding
echo ""
echo "💾 Step 10: Committing infrastructure files..."
git add \
    .env.example \
    tinko-console/.env.example \
    Dockerfile \
    tinko-console/Dockerfile \
    docker-compose.yml \
    outstanding_work.json \
    issues.yml \
    NEXT_STEPS.sh \
    || echo "⚠️  Git add failed - files may already be staged"

echo ""
echo "Run: git commit -m 'infra: docker-compose, env templates, security+worker scaffolds'"
echo ""
