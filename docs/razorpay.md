# Razorpay Integration Notes

## Webhook Verification

- Set `RAZORPAY_WEBHOOK_SECRET` in the API environment.
- The API verifies `X-Razorpay-Signature` as HMAC-SHA256 over the raw body.
- Processed events are stored idempotently in `psp_events` using a deterministic key: `razorpay:{event}:{payment_id|order_id}`.

### Example using stripe-like payload

```bash
export API=http://127.0.0.1:8010
export SECRET=shh
# Save payload.json with a Razorpay event body (payment.captured/order.paid)
python - <<'PY'
import json, hmac, hashlib, os, sys
body = open('payload.json','rb').read()
secret = os.environ.get('SECRET','shh')
sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
print(sig)
PY
# Use the printed signature below
curl -X POST "$API/v1/payments/razorpay/webhooks" \
  -H "X-Razorpay-Signature: REPLACE_WITH_SIG" \
  -H 'Content-Type: application/json' \
  --data-binary @payload.json
```

## Public Order Creation

- `POST /v1/payments/razorpay/orders-public` accepts `{ "ref": "TXN-..." }`.
- Returns `{ order_id, key_id, amount, currency }`. Use it with Razorpay Checkout on the console.

## Retry & Scheduling

- Persist a selected retry time via `PATCH /v1/recoveries/{id}/next_retry_at` with the recovery token as Bearer.
- Use the in-process runner for CI/local: `POST /v1/retry/trigger-due` when `FALLBACK_RETRY_RUNNER=true`.
