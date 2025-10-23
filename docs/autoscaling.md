# Autoscaling and Load Testing

This guide covers a minimal Horizontal Pod Autoscaler (HPA) configuration for the backend and a k6 smoke test to validate basic API responsiveness.

## HPA (Kubernetes)

Apply the HPA manifest:

```sh
kubectl apply -f infra/k8s/hpa-backend.yaml
```

Adjust `minReplicas`, `maxReplicas`, and the CPU utilization target as needed based on your workload.

## k6 Smoke Test

Install k6 locally, then run:

```sh
API_BASE_URL=http://127.0.0.1:8000 k6 run load/k6_smoke.js
```

This hits `/healthz` and `/v1/analytics/summary` to validate the API is healthy under light load.
