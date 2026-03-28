---
description: >-
  Apply a minimal, fast-tracked production fix with targeted verification and
  explicit scope control.
argument-hint: '[critical issue description]'
agent: 'agent'
tools:
  - execute
  - read
  - search
  - edit
  - codebase
---

# Hotfix

Use this prompt only for genuinely urgent production fixes.

Follow the skills:

- `.github/skills/repo-delivery/SKILL.md`
- `.github/skills/execution-environment/SKILL.md`

## Copilot-native usage

- Prefer the normal `/plan` -> `execute-plan` path for non-critical work.
- Keep the change minimal, targeted, and regression-aware.
