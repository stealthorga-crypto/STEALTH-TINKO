# 🚀 PSP-001 Quick Start Guide

## 1. Install Dependencies

```bash
cd Stealth-Reecovery
pip install stripe==11.1.1
```

## 2. Configure Environment

Add to `.env`:

```bash
# Stripe Test Keys (from https://dashboard.stripe.com/test/apikeys)
STRIPE_SECRET_KEY=sk_test_51...your_key_here
STRIPE_WEBHOOK_SECRET=whsec_...your_secret_here

# Frontend URL
BASE_URL=http://localhost:3000
```

## 3. Run Database Migration

```bash
alembic upgrade head
```

Or use quick table creation:

```bash
python -c "from app.db import engine, Base; Base.metadata.create_all(bind=engine)"
```

## 4. Start Backend Server

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 5. Test API Endpoints

### Get Auth Token

```bash
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

### Create Checkout Session

```bash
export TOKEN="your_jwt_token_here"

curl -X POST http://localhost:8000/v1/payments/stripe/checkout-sessions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_ref": "TXN-001",
    "amount": 5000,
    "currency": "usd",
    "customer_email": "customer@example.com"
  }'
```

Expected response:

```json
{
  "session_id": "cs_test_...",
  "payment_intent_id": "pi_...",
  "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_...",
  "expires_at": "2025-01-19T10:00:00Z"
}
```

### Create Payment Link

```bash
curl -X POST http://localhost:8000/v1/payments/stripe/payment-links \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_ref": "TXN-001",
    "amount": 5000,
    "currency": "usd"
  }'
```

### Check Session Status

```bash
curl http://localhost:8000/v1/payments/stripe/sessions/cs_test_123/status \
  -H "Authorization: Bearer $TOKEN"
```

## 6. Configure Stripe Webhook (Production)

In Stripe Dashboard → Developers → Webhooks:

1. Click "Add endpoint"
2. URL: `https://your-domain.com/v1/payments/stripe/webhooks`
3. Events: Select these events:
   - `checkout.session.completed`
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
4. Copy webhook signing secret to `STRIPE_WEBHOOK_SECRET` in `.env`

## 7. Test Webhooks Locally

Install Stripe CLI:

```bash
stripe listen --forward-to localhost:8000/v1/payments/stripe/webhooks
```

Trigger test webhook:

```bash
stripe trigger checkout.session.completed
```

## 8. Complete Integration Test

```bash
# 1. Create transaction (via dev endpoint or SQL)
curl -X POST http://localhost:8000/_dev/seed -H "Authorization: Bearer $TOKEN"

# 2. Create payment link
curl -X POST http://localhost:8000/v1/payments/stripe/checkout-sessions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"transaction_ref":"TXN-001","amount":5000,"currency":"usd"}'

# 3. Visit checkout URL in browser
# (Copy checkout_url from response)

# 4. Use Stripe test card: 4242 4242 4242 4242
# Any future expiry, any CVC

# 5. Check webhook fired
# Stripe CLI will show webhook received

# 6. Verify recovery status updated
curl http://localhost:8000/v1/recoveries/by_token/YOUR_TOKEN \
  -H "Authorization: Bearer $TOKEN"
# Status should be "completed"
```

## 9. Test Stripe Cards

**Success:** 4242 4242 4242 4242  
**Decline:** 4000 0000 0000 0002  
**3D Secure:** 4000 0027 6000 3184

## 10. Monitor Stripe Activity

- **Dashboard:** https://dashboard.stripe.com/test/payments
- **Logs:** https://dashboard.stripe.com/test/logs
- **Webhooks:** https://dashboard.stripe.com/test/webhooks

## Troubleshooting

### "Stripe API key not configured"

→ Set `STRIPE_SECRET_KEY` in `.env`

### "Invalid webhook signature"

→ Use Stripe CLI for local testing OR set correct `STRIPE_WEBHOOK_SECRET`

### "Transaction not found"

→ Create transaction first OR use correct `transaction_ref`

### Import errors

→ Run `pip install -r requirements.txt`

---

**Quick Health Check:**

```bash
# Verify imports
python -c "from app.services.stripe_service import StripeService; print('✅ OK')"

# Check endpoints
curl http://localhost:8000/healthz
```

**All working? You're ready to process payments! 🎉**
