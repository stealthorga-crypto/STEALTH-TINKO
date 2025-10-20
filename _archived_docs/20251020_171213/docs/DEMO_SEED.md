# Demo seeding helpers

These developer-only endpoints help you spin up a demo Transaction and Recovery Link for the payer flow quickly, without touching SQL or Stripe.

Base path: `/_dev`

## 1) Create a transaction

POST `/_dev/seed/transaction`

Query params:

- `ref` (string, default `ref_demo_1`): External transaction reference
- `amount` (int, default `1999`): Minor units (e.g., paise)
- `currency` (string, default `inr`)

Response:

- `{ ok: true, id, transaction_ref, amount, currency }`

Idempotent by `transaction_ref` — will return the same record if it already exists.

## 2) Create a recovery link for a transaction

POST `/_dev/seed/recovery_link`

Query params:

- `ref` (string, default `ref_demo_1`): Must match an existing transaction_ref (or one will be created if missing)
- `ttl_hours` (float, default `24`): Link expiry window

Response:

- `{ ok: true, attempt_id, token, url, expires_at, transaction_ref }`

The `url` points to the Payer UI route on `PUBLIC_BASE_URL`:

- `PUBLIC_BASE_URL` (env) default: `http://127.0.0.1:8000`
- For local Next.js console, set it to the console origin, e.g. `http://localhost:3000`.

## Notes

- These routes are mounted under the `_dev` tag and should not be exposed in production.
- They use SQLAlchemy models and the same DB connection as the API.
- The generated link uses the `/pay/retry/{token}` path expected by the console.
