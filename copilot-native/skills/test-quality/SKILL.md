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

## Guardrails

- Confirm the source file exists before calling a test missing.
- Match the project's mocking and assertion patterns in recommendations.
- Treat missing `await` on async assertions as a high-signal issue.
