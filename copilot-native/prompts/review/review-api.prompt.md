---
description: >-
  Specialist API and service compliance pass that applies backend review
  foundations and project-specific API patterns to the requested scope.
argument-hint: '[files or scope to review]'
agent: 'agent'
tools:
  - read
  - search
  - codebase
---

# Review API

Use this prompt when built-in `/review` is too broad and you want a targeted
backend compliance pass.

Follow the skills:

- `.github/skills/review-foundations/SKILL.md`
- `.github/skills/api-patterns/SKILL.md`

## Copilot-native usage

- Read `.github/copilot-instructions.md` first.
- Review against project patterns, not generic framework preferences.
