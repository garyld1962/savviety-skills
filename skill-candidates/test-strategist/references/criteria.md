# Test Strategist — Disposition Criteria

## Disposition Table

| Finding | Disposition | Override Conditions |
|---------|------------|---------------------|
| Test with no assertion | Blocking | — |
| Empty test body | Blocking | Placeholder with TODO + ticket reference |
| `test.skip` without explanation | Blocking | Has TODO comment with issue ref |
| `setTimeout` / `sleep` in test | Blocking | Intentional delay test (e.g., testing a debounce with fake timers) |
| Assertion on implementation detail | Non-blocking | Intentional contract assertion (e.g., verifying exact API call shape for audit) |
| Only happy path coverage | Non-blocking | Function has no error paths / trivial utility |
| Excessive mocking (4+) | Non-blocking | Each mock is a true external boundary (HTTP, DB, queue) |
| Very long test name | Discussion | — |
| No edge case coverage | Discussion | — |

## Blocking: What It Means

A blocking finding means the test provides false confidence — it passes when it should fail, or cannot possibly catch the bug it claims to cover. False-confidence tests are actively harmful: they appear in coverage reports and CI green checks while protecting nothing.

## Scope Rules

- **Apply to**: `*.test.*`, `*.spec.*`, `__tests__/` directories
- **Skip**: Source files unless checking cross-reference (error paths in source vs. test coverage)
- **Language notes**: Examples use Jest/Vitest syntax. Translate to pytest / Go testing / RSpec equivalents where appropriate.

## Judgment Notes

A weak assertion like `toBeTruthy()` on a boolean result may be acceptable if it's one of several assertions in a test that also checks specific values. Flag only when `toBeTruthy()` is the only assertion, or when the asserted value is inherently truthy (an object, an array).

Excessive mocking (4+) is a smell, not a rule. If each mock represents a genuine external system boundary (HTTP service, database, message queue, email provider), 4 mocks may be appropriate. Flag if any mocks are for internal module dependencies.
