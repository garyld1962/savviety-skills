---
description: >-
  Targeted test review that uses the shared review engine with coverage,
  behavior, async, and isolation focus using the project's real test
  conventions.
argument-hint: '[files or scope to review]'
agent: 'agent'
tools:
  - read
  - search
  - codebase
---

# Review Tests

Use this prompt when built-in `/review` is too broad and you want a targeted
test-quality pass.

Follow the skills:

- `.github/skills/review-engine/SKILL.md`
- `.github/skills/test-quality/SKILL.md`

## Routing

- Start from the `domain-review` lane and emphasize correctness, tests, async, and
  isolation concerns from `test-quality`.
- Only elevate to `professional-review` when the real issue is broader
  engineering judgment (for example, a test strategy that makes the system
  operationally unsafe to change).

## Copilot-native usage

- Detect the test framework and file layout before reviewing.
- Keep findings behavior-focused and evidence-based.
