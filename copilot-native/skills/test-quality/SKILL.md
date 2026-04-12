---
name: test-quality
description: Test review rubric for behavior-focused coverage, async correctness, isolation, and meaningful test naming.
---

# Test Quality

Use this skill for specialist test reviews.

## Review focus

- detect the test framework and file layout first
- find real coverage gaps by checking source files against test files
- favor behavior assertions over brittle implementation-detail assertions
- verify async assertions are awaited correctly
- check for shared mutable state, leaked mocks, real network calls, or other
  isolation problems
- require meaningful `describe` and `it` names

## Examples

- **Missing coverage claim:** Before saying a source file is untested, confirm
  the source file exists and look for the nearest real test file or test suite
  that exercises it.
- **Async defect:** If a test forgets to await an async assertion or promise,
  treat it as a high-signal correctness issue rather than a naming or style nit.

## Guardrails

- Confirm the source file exists before calling a test missing.
- Match the project's mocking and assertion patterns in recommendations.
- Treat missing `await` on async assertions as a high-signal issue.

## Do Nots

- Do not infer a missing-test problem from filename patterns alone.
- Do not prefer implementation-detail assertions over behavior assertions just
  because they are easier to write.
- Do not downgrade isolation leaks or async false positives into cosmetic
  feedback.

## Closed Decisions

- The repo's actual test framework and local test patterns are the baseline.
- Behavior-focused coverage is preferred over brittle implementation coupling.
- Async correctness and isolation issues outrank naming polish.
- Source existence must be confirmed before a missing-test finding is valid.
