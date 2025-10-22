# Cloud DB Baseline (Postgres)

This project can run against a managed Postgres instance in staging/production. Configure the connection via environment variables.

## Required env vars

- DATABASE_URL: Postgres connection string
- JWT_SECRET: JWT signing secret
- STRIPE_SECRET_KEY: Stripe API key (test or live)
- STRIPE_WEBHOOK_SECRET: Stripe webhook signing secret
- REDIS_URL: Redis connection (for Celery)

### DATABASE_URL format

For Postgres on a managed service:

postgresql://<user>:<password>@<host>:<port>/<database>

Example (staging):

postgresql://tinko_stg:supersecret@db.example.com:5432/tinko_staging

## Local migrations (smoke)

Optionally verify migrations against your DATABASE_URL:

```
# optional, run locally
alembic upgrade head
```

Ensure your app process reads the DATABASE_URL from the environment (see `app/db.py`).
