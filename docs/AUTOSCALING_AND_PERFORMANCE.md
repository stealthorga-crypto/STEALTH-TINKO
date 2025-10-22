# Autoscaling and Performance

This document outlines a pragmatic baseline for scaling the Tinko Recovery stack and improving performance in production-like environments.

## Backend API (FastAPI)
- Container runtime: uvicorn[standard]
- Concurrency: prefer multiple replicas over high per-pod thread counts.
- Suggested settings:
  - Processes: 2–4 per node (or rely on orchestration to scale replicas)
  - Workers: use `--workers $(nproc)` for CPU-bound endpoints; most endpoints are I/O-bound
  - Keep-alive: `--http keep-alive 75`
- Health probes: `/healthz` for liveness, `/readyz` for readiness

## Task Workers (Celery)
- Broker/Backend: Redis
- Concurrency: start with `--concurrency=2` per pod and scale replicas horizontally
- Acks late: enable for idempotent tasks to improve resilience
- Prefetch: reduce with `--prefetch-multiplier=1` for fairness in bursty work
- Queue separation: place retry/notification queues separately if needed

## Database (Postgres)
- Connection pooling: use PgBouncer in transaction mode
- Pool size per app instance: 5–10 connections
- Long-running queries: avoid; use read-only reconciliation patterns
- Partitioning: monthly stubs available; extend partitions for high-volume tables

## Caching
- Redis memory: reserve 25–50% headroom for spikes
- Key TTLs: assign expiration to ephemeral entries when possible

## Observability
- Sentry: enable DSN and sample rates via env
- Structured logs: ensure `LOG_LEVEL` is set appropriately (INFO/ERROR in prod)
- Metrics sink: optional analytics sink is available; keep disabled unless required

## Horizontal Pod Autoscaler (K8s)
- Targets: CPU 60–70% or request rate (via service mesh/metrics adapter)
- Separate HPAs: API and Workers scale independently
- Readiness gates: ensure workers expose a lightweight `/healthz`

## Performance Testing
- Smoke tests: `smoke_test.py` validates core endpoints
- Load tests: use k6 or Locust to simulate retry/notification flows
- Bottlenecks to watch:
  - Email/SMS providers latency
  - Stripe API round-trips (use idempotency keys)
  - Database N+1 patterns on analytics endpoints

## Environment Variables Cheat-Sheet
- API: `LOG_LEVEL`, `ENVIRONMENT`
- Workers: `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, concurrency flags
- DB: `DATABASE_URL` (use managed Postgres), PgBouncer connection string
- Observability: `SENTRY_*`
- Optional: `ANALYTICS_SINK_*`

## Next Steps
- Replace partitioning stubs with real partitions for hot tables
- Add metrics exporter (Prometheus) and dashboards (Grafana)
- Implement per-tenant rate limiting if needed
