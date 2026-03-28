---
description: >-
  Specialist test review that checks coverage gaps, behavior focus, async
  correctness, and isolation using the project's real test conventions.
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

- `.github/skills/review-foundations/SKILL.md`
- `.github/skills/test-quality/SKILL.md`

## Copilot-native usage

- Detect the test framework and file layout before reviewing.
- Keep findings behavior-focused and evidence-based.
