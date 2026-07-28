# Stripe Review — Report Format

---

## Template

```
## Stripe Review — [branch or description]
[N files reviewed · N findings: N blocking, N non-blocking, N discussion]

---

### Blocking

#### `app/api/webhook/route.ts:8` — Missing webhook signature verification
**Found**: `const body = await req.json()`
**Risk**: No `constructEvent` call — any attacker can POST fake payment events. Granting access without payment is fraud-enabling.
**Fix**:
```ts
const rawBody = await req.text()
const sig = req.headers.get('stripe-signature')!
const event = stripe.webhooks.constructEvent(rawBody, sig, process.env.STRIPE_WEBHOOK_SECRET!)
```

#### `lib/payments.ts:34` — Missing idempotency key
**Found**: `await stripe.paymentIntents.create({ amount, currency, customer })`
**Risk**: Network retry creates a duplicate charge. Customer is charged twice.
**Fix**: Add `{ idempotencyKey: \`payment_\${orderId}\` }` as second argument.

---

### Non-blocking

#### `app/api/webhook/route.ts:45` — Webhook slow to return 200
**Found**: `await sendWelcomeEmail(userId); return new Response(null, { status: 200 })`
**Impact**: If email send takes >5s, Stripe retries — email sent twice, webhook processed twice.
**Suggestion**: Queue the email job, return 200 immediately, process asynchronously.

---

### Discussion

#### `lib/stripe.ts:12` — Currency hardcoded as USD
**Found**: `currency: 'usd'`
**Note**: Fine for single-market products. Flag if international support is on the roadmap — configurable currency is a one-time change easier to do now.

---

### Looks Good
- Idempotency key on subscription creation in `lib/subscriptions.ts` — correct pattern
[or: All N remaining checks passed.]
```

---

## Formatting Rules

**Found field**: exact line from the diff. Max 3 lines; append `(N total — showing 3)` if more.

**Risk field** (blocking): state the financial or security consequence first. "Fake payment events" beats "missing verification."

**Fix field** (blocking): show the corrected code. Multi-line is fine for webhook signature pattern — it's the most critical fix.

**No commands in the report**: show findings, not the grep that found them.

**No preamble**: start directly with `## Stripe Review` header.

**Collapse passed checks**: if more than 8 checks passed with no findings, emit `All N remaining checks passed.`

**Rotate key instruction**: if a live secret key (`sk_live_` or `whsec_`) is found hardcoded, include a note: "Rotate this key in the Stripe dashboard immediately — treat it as compromised."

**Empty diff**: emit `No Stripe concerns — no payment code in diff.` and stop.

---

## Comment Style

- **Blocking**: lead with the financial consequence. "Customer charged twice" beats "missing idempotency key."
- **Non-blocking**: frame as reliability gap. "Webhook processed twice" beats "should queue work."
- **Discussion**: acknowledge author context. "Fine for single-market" beats "you should make this configurable."
- Never: "you should have", "this is wrong", "why did you". The code is the subject, not the author.
