# Observability Setup Guide

## Structured Logging

### Backend (Structlog)

All logs are JSON-formatted with structured fields:

```python
from app.logging_config import get_logger

logger = get_logger(__name__)

# Log with structured data
logger.info("user_registered",
    user_id=user.id,
    org_id=user.org_id,
    email=user.email
)

# Errors automatically include stack traces
logger.error("payment_failed",
    transaction_id=tx.id,
    error_code=error.code,
    exc_info=True
)
```

### Log Context

Request-scoped context is automatically added to all logs:

- `request_id`: Unique ID for request tracing
- `method`: HTTP method (GET, POST, etc.)
- `path`: Request path
- `user_id`, `org_id`, `user_role`: Added after authentication

### Example Log Output

```json
{
  "event": "payment_processed",
  "timestamp": "2025-01-15T10:30:45.123Z",
  "level": "info",
  "logger": "app.routers.payments",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "method": "POST",
  "path": "/v1/payments/checkout",
  "user_id": 123,
  "org_id": 456,
  "transaction_id": "tx_abc123",
  "amount_cents": 1999,
  "app": "stealth-recovery",
  "environment": "production"
}
```

## Error Tracking (Sentry)

### Backend Setup

1. Create Sentry project at https://sentry.io
2. Copy DSN from project settings
3. Set environment variable:
   ```bash
   export SENTRY_DSN=https://xxxxx@sentry.io/12345
   export ENVIRONMENT=production
   ```

Sentry is automatically initialized in `app/main.py` and captures:

- Unhandled exceptions
- FastAPI route errors
- SQLAlchemy database errors
- Performance traces (10% sample rate)

### Frontend Setup

1. Install Sentry SDK:

   ```bash
   cd tinko-console
   npm install @sentry/nextjs
   ```

2. Set environment variable:

   ```bash
   NEXT_PUBLIC_SENTRY_DSN=https://xxxxx@sentry.io/12345
   NEXT_PUBLIC_ENVIRONMENT=production
   ```

3. Initialize in app layout:

   ```typescript
   import { initSentry } from "@/lib/sentry";

   initSentry();
   ```

4. Track user context:

   ```typescript
   import { setSentryUser } from "@/lib/sentry";

   // After user login
   setSentryUser({
     id: user.id,
     email: user.email,
     org_id: user.org_id,
   });
   ```

### Manual Error Capture

```typescript
import { captureException, captureMessage } from "@/lib/sentry";

try {
  // risky operation
} catch (error) {
  captureException(error, {
    component: "PaymentForm",
    transaction_id: tx.id,
  });
}

// Log important events
captureMessage("Critical inventory threshold reached", "warning");
```

## Request Tracing

Every HTTP request gets a unique `request_id`:

1. **Auto-generated**: If not provided, UUID is created
2. **Client-provided**: Pass `X-Request-ID` header to track client-to-server requests
3. **Response header**: Server returns `X-Request-ID` in response
4. **Logs**: All logs for a request include the same `request_id`

### Tracing Flow

```
Client Request
  ↓ (X-Request-ID: abc-123 or generated)
Middleware: Bind request_id to log context
  ↓
Route Handler: All logs include request_id
  ↓
Database Queries: Logged with request_id
  ↓
Response: X-Request-ID header returned
```

### Finding Logs for a Request

```bash
# In production logs (JSON format)
cat logs.json | grep '"request_id":"550e8400-e29b-41d4-a716-446655440000"'

# In development (human-readable)
docker compose logs backend | grep 550e8400-e29b-41d4-a716-446655440000
```

## Production Monitoring

### Recommended Stack

1. **Logs**: Ship JSON logs to Datadog, Splunk, or ELK
2. **Errors**: Sentry for error tracking and alerting
3. **Metrics**: Prometheus + Grafana for system metrics
4. **APM**: Sentry Performance or Datadog APM

### Key Metrics to Track

- Request rate (requests/sec)
- Error rate (%)
- Response time (p50, p95, p99)
- Database query time
- Recovery success rate
- Payment completion rate

### Sample Rates

Configured via environment variables:

```bash
# Sentry performance tracing (10% of requests)
SENTRY_TRACES_SAMPLE_RATE=0.1

# Sentry profiling (10% of traces)
SENTRY_PROFILES_SAMPLE_RATE=0.1

# Adjust for high-traffic production
SENTRY_TRACES_SAMPLE_RATE=0.01  # 1% in production
```

## Debugging Tips

### Find all logs for a user

```bash
cat logs.json | grep '"user_id":123'
```

### Find all errors in last hour

```bash
cat logs.json | grep '"level":"error"' | grep "$(date -u +%Y-%m-%d)" | tail -100
```

### Trace a failed payment

```bash
# Find request_id from transaction logs
cat logs.json | grep '"transaction_id":"tx_abc123"'
# Then find all logs for that request
cat logs.json | grep '"request_id":"..."'
```

### Local Development

In development mode:

- Logs are pretty-printed to console
- Sentry is disabled (only enabled in production)
- All requests are traced
