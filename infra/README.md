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

## Kubernetes baseline manifests

Minimal Deployment/Service and HPA for the backend are provided under `infra/k8s` using Kustomize.

- Deployment: `infra/k8s/deployment-backend.yaml` (container listens on 8000)
- Service: `infra/k8s/service-backend.yaml` (ClusterIP on 8000)
- HPA: `infra/k8s/hpa-backend.yaml` (targets `tinko-backend` deployment)
- Config: `infra/k8s/configmap-backend.yaml`
- Secret: `infra/k8s/secret-backend.yaml` (placeholder values)
- Kustomization: `infra/k8s/kustomization.yaml`

Usage (example):

```
# Preview rendered manifests
kubectl kustomize infra/k8s

# Apply to a cluster
kubectl apply -k infra/k8s

# Override image tag
kubectl apply -k infra/k8s --server-side
```

Notes:

- The default image in kustomization is a placeholder (`ghcr.io/your-org/stealth-recovery-backend:latest`). Update it to your registry.
- The Deployment uses an `emptyDir` at `/app/data` for SQLite. For production, switch to Postgres by setting `DATABASE_URL` in the ConfigMap/Secret and mounting no local persistence.
- Probes hit `/readyz` and `/healthz` endpoints exposed by the FastAPI app.
