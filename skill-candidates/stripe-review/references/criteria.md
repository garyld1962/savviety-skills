# Stripe Review — Criteria

---

## Dispositions

| Disposition | Meaning | PR Action |
|-------------|---------|-----------|
| **Blocking** | Direct financial risk: fraud, double-charge, missed payment, or secret exposure | Request changes — do not merge |
| **Non-blocking** | Reliability gap; doesn't stop merge but should be addressed promptly | Comment with suggestion |
| **Discussion** | Tradeoff or configuration question. No required action. | Comment as FYI |
| **Praise** | Good payment safety practice worth calling out | Inline compliment |

---

## Disposition by Check

### Blocking

| Check | Why |
|-------|-----|
| Missing webhook signature verification | Anyone can POST fake "payment succeeded" events. Direct path to fraud. |
| Webhook using parsed JSON body | Signature verification will silently fail in production. Webhooks stop working. |
| Missing idempotency key on payment creation | Network retries create duplicate charges. Direct financial harm to customers. |
| Fulfillment in payment creation (not webhook) | Race condition — payment may succeed but fulfillment code may not run. User charged, no access. |
| Hardcoded Stripe secret key | Secret in source control. Rotate immediately. |
| Publishable key used server-side | Wrong key type; charges will fail or behave incorrectly. |
| Hardcoded webhook secret | Secret exposed in source. Rotate immediately. |

### Non-blocking

| Check | Why |
|-------|-----|
| No retry logic on API calls | Stripe has transient errors. No retry means silent operation loss. |
| Customer ID not stored | Duplicate customers in Stripe; broken customer history and portal access. |
| Webhook slow to return 200 | Stripe retries after 5 seconds. Slow handlers cause duplicate processing. |
| Missing event type check | Wrong handler logic fires on unrelated webhook events. |

### Discussion

| Check | Why |
|-------|-----|
| Test keys in non-test files | Confirm loaded from env — not a blocker if they are. Discuss env separation. |
| Hardcoded USD currency | Blocks international expansion. Not urgent unless multi-currency is in scope. |
| Missing webhook secret startup check | Fails silently; better to crash on startup if misconfigured. |

---

## Scope Rules

**Do not flag**:
- Issues in `*.test.*`, `*.spec.*`, `__tests__/` for Tier 2+
- Hardcoded test keys in `*.test.*` or `*.spec.*` files (accepted in test fixtures)
- Issues in lines not in the diff (pre-existing code)
- `pk_` keys on client-side files (publishable key is intentionally public)

**Always flag regardless of file**:
- Live secret keys (`sk_live_`) in any source file
- Webhook handlers missing `constructEvent` / `construct_event`
- Raw card data storage (`card_number`, `cardNumber`, `cc_number`)

---

## False Positive Rate Note

Stripe-specific identifiers are highly distinctive. When found in new code:
- `constructEvent` — almost always a real webhook handler
- `idempotencyKey` / `idempotency_key` — almost always a real payment call
- `sk_live_` / `whsec_` — hardcoded secrets, never a false positive in source code

Treat these as confirmed findings. The only legitimate exception is test fixtures that mock Stripe responses.
