# Tinko — Failed Payment Recovery (MVP Spec)

## Problem
Customers attempt an online payment (UPI/card/netbanking). Gateway returns failure or pending, and the order is abandoned. We will recover revenue by diagnosing, retrying safely, and guiding the user.

## Goals (MVP)
1. Receive a standardized `payment_failed` webhook event.
2. De-duplicate & store event with correlation IDs.
3. Classify failure (issuer decline, 3DS/OTP timeouts, UPI pending, network).
4. Recommend & trigger a safe retry path (same method vs alternate).
5. Notify user with a templated message containing a 1-tap retry link.
6. Track recovery outcomes (recovered, partial, dropped).

## Core Flow
1) Gateway → Tinko: `payment_failed` (JSON)
2) Tinko: de-dupe by `event_id` or `(order_id, attempt_id)`
3) Tinko: classify reason (rules)
4) Tinko: generate retry options
5) Tinko: notify user + signed retry URL
6) User clicks → merchant payment page (pre-filled)
7) Gateway callback → Tinko: `payment_succeeded` / `payment_failed`
8) Tinko marks outcome; metrics updated

## Acceptance
- Webhook stored in <200ms
- Idempotent (same event ≥2x → single row)
- Retry advice for top failure categories
- Recovery rate = recovered / failed is queryable
