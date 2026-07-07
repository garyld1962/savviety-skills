---
description: >-
  Targeted API and service review that uses the shared review engine with API,
  validation, auth, async, and contract focus for the requested scope.
argument-hint: '[files or scope to review]'
agent: 'agent'
tools:
  - read
  - search
  - codebase
---

# Review API

Use this prompt when built-in `/review` is too broad and you want a targeted
backend review pass.

Follow the skills:

- `.github/skills/review-engine/SKILL.md`
- `.github/skills/api-patterns/SKILL.md`

## Routing

- Start from the `domain-review` lane with `profile: code-comprehensive`.
- Emphasize API contract, validation, auth, logging, async behavior, and service
  integration risks from `api-patterns`.
- If the main concern is broader engineering-choice quality rather than a direct
  defect, say so and elevate to `professional-review`.

## Copilot-native usage

- Read `.github/copilot-instructions.md` first.
- Review against project patterns, not generic framework preferences.
