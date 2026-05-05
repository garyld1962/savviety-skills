# Test Strategist — Sharp Edges

---

## Testing Implementation Not Behavior

**Severity**: High
**Situation**: Tests assert on internal method calls, SQL query strings, or DOM structure rather than observable outputs. Every refactor breaks tests even when behavior is correct.

```js
// BAD — tests break if you rename the method or change the query
expect(db.query).toHaveBeenCalledWith('SELECT * FROM users WHERE id = ?', [123])

// GOOD — survives refactoring
const user = await service.getUser(123)
expect(user.name).toBe('Alice')
```

**Fix**: Assert on outputs and side effects visible to callers. The contract is what the function promises, not how it delivers.

---

## Coverage Theater

**Severity**: Critical
**Situation**: 95% coverage. Management is happy. Production bugs keep shipping. Coverage measures lines executed, not behavior verified. You can hit 100% with zero useful assertions.

```js
// Achieves coverage, proves nothing
it('runs calculateDiscount', () => {
  expect(calculateDiscount(100, 'premium')).toBeTruthy()  // passes even if result is 1
})
```

**Fix**: Ask "would this test fail if the code returned the wrong value?" If not, the assertion is too weak. Test specific values, not truthiness.

---

## Sleep/setTimeout in Tests

**Severity**: High (Blocking)
**Situation**: Fixed delays make tests slow and non-deterministic. Works on a fast machine, fails in CI under load.

```js
// BAD — flaky
await new Promise(resolve => setTimeout(resolve, 2000))
expect(element).toBeVisible()

// GOOD — deterministic
await waitFor(() => expect(element).toBeVisible())
```

**Fix**: Wait for conditions, not time. Use `waitFor`, polling utilities, or event-based signals.

---

## Testing the Framework, Not Your Code

**Severity**: Medium
**Situation**: Tests that verify React renders a button, that Express returns 200 for a valid route, that an ORM can query — you're testing library behavior you don't own.

**Fix**: Test your logic within the framework, not the framework itself. If the test would pass with any component/any handler/any query, it's testing the wrong thing.

---

## Mocking Everything

**Severity**: High
**Situation**: Eight mocks in one test. The test passes but you've verified that your code works with your mocks — not with reality. Mock drift accumulates silently.

```js
// Eight jest.mock() calls at the top of a "unit" test is a smell
jest.mock('../db')
jest.mock('../cache')
jest.mock('../emailService')
jest.mock('../analyticsService')
// ... etc
```

**Fix**: If you need this many mocks, consider an integration test with real (or in-memory) dependencies instead. Mock at system boundaries, not at every internal call. The fewer mocks, the more confidence the test provides.
