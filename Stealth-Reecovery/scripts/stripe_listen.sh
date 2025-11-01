#!/bin/bash
# Stripe CLI webhook listener for local development
# Forwards Stripe events to the backend webhook endpoint

echo "Starting Stripe CLI webhook listener..."
echo "Forwarding events to: http://localhost:8000/v1/webhooks/stripe"
echo ""
echo "This will listen for the following events:"
echo "  - checkout.session.completed"
echo "  - payment_intent.succeeded"
echo "  - payment_intent.payment_failed"
echo ""

stripe listen \
  --events checkout.session.completed,payment_intent.succeeded,payment_intent.payment_failed \
  --forward-to http://localhost:8000/v1/webhooks/stripe

# After running this script, copy the webhook signing secret
# and set it as STRIPE_WEBHOOK_SECRET in your .env file
