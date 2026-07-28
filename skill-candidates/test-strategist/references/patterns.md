# Test Strategist — Patterns

---

## Test Pyramid vs. Trophy

```
Classic Pyramid (Mike Cohn):        Modern Trophy (Kent C. Dodds):
        /E2E\                               /E2E\
       /------\                            /------\
      /Integr- \                          / Integr-\   ← MORE of these
     /  ation   \                        /  ation   \
    /------------\                      /------------\
   /    Unit      \  ← MOST            /    Unit      \  ← FEWER
  /__________________\                /__________________\

Pyramid: many unit, few integration, fewer E2E.
Trophy: few unit (complex logic only), more integration, few E2E.
```

**When to lean pyramid**: Library/utility code with many edge cases. Pure algorithms. State machines. Logic that has no meaningful integration surface.

**When to lean trophy**: Web services, APIs, CRUD apps, anything where the bug is usually "wrong query" or "wrong field mapping" — not a logic error in a pure function. Most real-world web apps fall here.

**Rule**: Most bugs are integration bugs. If your test shape doesn't match your bug shape, you'll miss them.

---

## Characterization Tests (Before Refactoring)

Write before touching legacy code. Capture current behavior — including edge cases you don't understand yet.

```js
test('calculateDiscount current behavior', () => {
  expect(calculateDiscount(100, 'premium')).toBe(85)
  expect(calculateDiscount(100, 'basic')).toBe(100)
  expect(calculateDiscount(0, 'premium')).toBe(0)
  expect(calculateDiscount(-1, 'basic')).toBe(0)  // surprising? document it
})
// Now refactor. If a test breaks, you changed behavior — decide if that's intentional.
```

---

## Contract Tests (For API Boundaries)

When mocking an external service, test your mock against the real thing periodically. Otherwise the mock drifts.

```js
// consumer-contract.test.ts — runs in CI with real service
describe('PaymentService contract', () => {
  it('charge returns transaction id on success', async () => {
    const result = await realPaymentService.charge({ amount: 100, currency: 'usd' })
    expect(result.transactionId).toMatch(/^txn_/)
  })
})

// unit tests mock PaymentService — but the contract test keeps the mock honest
```

---

## Parameterized Tests (For Edge Case Coverage)

```js
test.each([
  [0,    'premium', 0  ],
  [100,  'premium', 85 ],
  [100,  'basic',   100],
  [-1,   'premium', 0  ],  // negative input
  [null, 'premium', 0  ],  // null guard
])('calculateDiscount(%s, %s) → %s', (amount, tier, expected) => {
  expect(calculateDiscount(amount, tier)).toBe(expected)
})
```

Forces you to enumerate edge cases explicitly. Failure message shows exactly which case broke.

---

## Test-as-Documentation Pattern

A test suite is the most accurate documentation in the codebase — it's executable and kept honest by CI. Write test names that form a specification:

```
UserService
  createUser
    ✓ returns created user with generated id
    ✓ hashes password before saving
    ✓ throws ValidationError when email is missing
    ✓ throws ConflictError when email already exists
    ✓ sends welcome email after successful creation
```

The test names become the spec. Anyone reading the test file knows what the function promises without reading the implementation.

---

## When to Skip Tests

Some code genuinely doesn't need tests — don't cargo-cult coverage:

- Simple getters/setters with no logic
- Configuration objects
- Thin wrappers around stable libraries (you'd be testing the library)
- Glue code that connects two tested pieces with no logic of its own
- Code that will be deleted within the sprint

Coverage mandates cause test theater. Test where bugs hide, not everywhere.
