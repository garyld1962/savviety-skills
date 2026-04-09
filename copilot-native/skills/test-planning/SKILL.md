---
name: test-planning
description: TDD-first planning rubric for generating test specifications and validating test readiness before implementation.
---

# Test Planning

Use this skill when creating or refreshing a test plan before or around
implementation.

## Relationship to Copilot built-ins

- Use this skill when a generic planning pass is not enough because the team
  wants tests to define the contract first.
- Use built-in `/plan` for overall implementation planning; use this skill for
  test-specific decomposition.

## Discovery steps

- detect the test framework and file naming conventions
- read at least one existing test file before generating new test specs
- verify import paths, source signatures, and types from the real codebase
- prefer project conventions over generic testing advice

## Plan mode

Generate test specifications as executable stubs or clearly structured cases
that cover:

- happy paths
- required validation
- error paths
- edge cases
- lifecycle or state transitions when real state exists

## Validate mode

When validating an existing suite, report:

- pass/fail/todo counts
- major coverage gaps
- framework-specific issues such as missing async awaits

## Refresh mode

When implementation changed after the original plan:

- re-read the changed code
- refresh stale specs
- keep the test plan aligned with current signatures and behavior

## Dependency classification

Classify each dependency to determine the testing approach:

| Category | Testing Strategy | Example |
|----------|-----------------|---------|
| **In-process** | Test directly — no mocks | Validation, transforms, calculations |
| **Local-substitutable** | Use real substitute — higher fidelity than mocks | PGLite for Postgres, in-memory FS |
| **Remote but owned** | Ports & Adapters — inject in-memory adapter | Your own API services, queues |
| **True external** | Mock at boundary — only valid mock target | Stripe, SendGrid, AWS S3 |

Do NOT mock in-process or local-substitutable dependencies — mocks hide real bugs.

## Guardrails

- Do not invent framework, file layout, or API signatures.
- Do not require file writing if the user only wants a plan in chat.
- Keep the plan behavior-focused, not implementation-coupled.
