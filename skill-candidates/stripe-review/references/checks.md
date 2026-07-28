# Stripe Review — Checks

All checks run against added lines only (see SKILL.md Step 2 for extraction command).

---

## Tier 1 — Auto-Flag (Financial Risk / Security)

Run against all files identified as Stripe-related.

### Webhook Handler Missing Signature Verification

```bash
grep -n "stripe-signature\|stripe_signature\|constructEvent\|webhook_secret\|WEBHOOK_SECRET" <file> | head -5
```

If the file is a webhook handler (filename contains `webhook`, or it handles POST from Stripe) and `constructEvent` (JS/TS) or `stripe.Webhook.construct_event` (Python) is absent from the file, flag as missing verification.

### Webhook Using Parsed JSON Instead of Raw Body

**JS/TS**:
```bash
grep -n "req\.json()\|await request\.json()\|JSON\.parse(req\.body)" <file> | head -5
```

**Python**:
```bash
grep -n "request\.get_json()\|request\.json\b" <file> | head -5
```

Flag if a webhook handler uses parsed JSON. Signature verification requires the raw bytes. The correct approach is `req.text()` (Next.js App Router), `express.raw()` middleware (Express), or `request.data` / `request.get_data()` (Flask).

### Missing Idempotency Key on Charge / Payment Creation

**JS/TS**:
```bash
grep -nE "(paymentIntents|charges|subscriptions)\.create\(" <file> | head -10
```

For each match, check ±10 lines for `idempotencyKey`. Flag if absent. Double-charges on network retry are a direct financial loss and customer trust issue.

**Python**:
```bash
grep -nE "stripe\.(PaymentIntent|Charge|Subscription)\.create\(" <file> | head -10
```

Check for `idempotency_key=` parameter. Flag if absent.

### Fulfillment Logic in Payment Intent Creation (Not in Webhook)

```bash
grep -nE "(paymentIntents|checkout\.sessions)\.create" <file> | head -5
```

If the same function/block that calls `create` also calls fulfillment logic (grant access, update subscription, send confirmation email), flag. Fulfillment must run in the `payment_intent.succeeded` or `checkout.session.completed` webhook handler — not at creation time.

### Hardcoded Stripe Secret Key

```bash
grep -nE "sk_(test|live)_[a-zA-Z0-9]{20,}" <file> | grep -v "process\.env\|os\.environ\|os\.getenv\|secrets\." | head -5
```

Flag any literal `sk_test_` or `sk_live_` key in source. Always blocking — rotate immediately if found in a committed file.

### Publishable Key Used Server-Side for Charges

```bash
grep -nE "pk_(test|live)_[a-zA-Z0-9]{20,}" <file> | grep -v "PUBLISHABLE\|publishable\|client\|frontend\|browser" | head -5
```

Flag `pk_` keys in server-side payment creation code. Publishable keys cannot authenticate server API calls — these will silently fail or expose the wrong key type.

### Hardcoded Webhook Secret

```bash
grep -nE "whsec_[a-zA-Z0-9]{20,}" <file> | grep -v "process\.env\|os\.environ\|os\.getenv" | head -5
```

Flag literal `whsec_` values in source code.

---

## Tier 2 — Judgment Required

### No Retry Logic on Stripe API Calls

```bash
grep -nE "await stripe\.[a-zA-Z]+\.[a-zA-Z]+\(|stripe\.[A-Z][a-zA-Z]+\.create\(" <file> | head -10
```

Check ±10 lines for try/catch with retry logic or error type checking (`StripeConnectionError`, `rate_limit` error code). Flag if absent — Stripe has transient failures; no retry means lost operations.

### Stripe Customer ID Not Stored

```bash
grep -nE "customers\.create\(|Customer\.create\(" <file> | head -5
```

If a customer is created but the resulting `customer.id` is not stored to a database, flag. Not storing the customer ID forces re-creation on every checkout, duplicating customers in Stripe.

### Webhook Handler Not Returning 200 Quickly

```bash
grep -nE "(await|yield)\s+\w+.*\n.*(return|res\.send|res\.json)" <file> | head -5
```

Flag webhook handlers that perform heavy async work (DB writes, email sends, external API calls) before returning a response. Stripe retries webhooks that don't respond within 5 seconds. Correct pattern: verify signature, queue the event, return 200.

### Missing Event Type Check in Webhook Switch

```bash
grep -n "event\.type\|event\[.type.\]" <file> | head -5
```

If the webhook handler processes `event` without checking `event.type`, flag. Handling all event types indiscriminately causes wrong logic to fire on unrelated events.

---

## Tier 3 — Discussion

### Test Keys in Non-Test Files

```bash
grep -nE "sk_test_[a-zA-Z0-9]+|pk_test_[a-zA-Z0-9]+" <file> | head -5
```

Flag in non-test files as a discussion point about environment separation. Test keys are not the blocking concern (only live keys in source are blocking), but confirm they are loaded from environment variables.

### Currency Hardcoded Instead of Configurable

```bash
grep -nE "currency:\s*['\"]usd['\"]|currency=['\"]usd['\"]" <file> | head -5
```

Flag hardcoded `"usd"` as a discussion point for international support. Not blocking unless multi-currency is an explicit requirement.

### Missing Webhook Endpoint Registration Check

```bash
grep -n "STRIPE_WEBHOOK_SECRET\|webhook_secret" <file> | head -5
```

If the webhook secret is referenced but no startup check validates it is set, note as a discussion point. Missing secret causes silent auth failures in production.
