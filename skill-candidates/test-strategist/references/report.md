# Test Strategist — Report Format

---

## Template

```
## Test Quality Review — [branch or description]
[N test files reviewed · N findings: N blocking, N non-blocking, N discussion]

---

### 🚫 Blocking

#### `tests/order.test.ts:34` — Skipped test, no explanation
**Found**: `it.skip('calculates discount for premium users', async () => {`
**Risk**: Silently excluded from CI. A broken feature can ship without anyone knowing this test exists.
**Fix**: Add reason: `it.skip('calculates discount — TODO: #1234 fix after pricing refactor', ...)`

---

#### `tests/auth.test.ts:67` — Sleep-based timing dependency
**Found**: `await new Promise(resolve => setTimeout(resolve, 2000))`
**Risk**: Passes when machine is fast, fails under CI load. Trains developers to retry rather than investigate.
**Fix**: `await waitFor(() => expect(screen.getByText('Success')).toBeVisible())`

---

### ⚠️ Non-blocking

#### `tests/user.test.ts:18` — Assertion on implementation detail
**Found**: `expect(db.query).toHaveBeenCalledWith('SELECT * FROM users WHERE id = ?', [123])`
**Impact**: Test breaks if query is refactored, even when behavior is correct.
**Suggestion**: `const user = await service.getUser(123); expect(user.name).toBe('Alice')`

---

### 💬 Discussion

#### `tests/payment.test.ts` — No error path coverage
**Found**: 8 tests, all happy path (`success`, `works`, `creates`)
**Note**: `processPayment` has explicit handling for `InsufficientFunds` and `CardDeclined`. These paths are untested.

---

### ✅ Looks Good
- Parameterized edge cases in `tests/discount.test.ts` — covers null, negative, boundary values
- `beforeEach` cleanup in `tests/db.test.ts` — no shared state between tests
[or: All N remaining checks passed.]
```

---

## Formatting Rules

**Found field**: Show the exact line from the diff. Max 3 lines; append `(N total — showing 3)` if more.

**Risk field** (blocking): State the failure mode, not the rule. "Trains developers to retry" beats "anti-pattern."

**Suggestion field** (non-blocking): Show the alternative code. Do not describe it — show it.

**No preamble**: Start directly with the `## Test Quality Review` header.

**No commands in the report**: Show findings, not the grep commands that found them.

**Collapse passed checks**: If >8 checks passed with no findings, write `All N remaining checks passed.` — do not enumerate.

**Praise sparingly**: Note genuinely good decisions — parameterized tests, isolated state, contract tests. Omit if there are blocking findings.

**Empty diff or no test files changed**: Emit `No test files in diff — skipping test quality checks.` and stop.
