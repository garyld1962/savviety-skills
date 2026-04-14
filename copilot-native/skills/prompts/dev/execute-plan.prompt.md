---
description: >-
  Execute an accepted implementation plan in dependency order using the repo's
  real commands and verification flow.
argument-hint: '[path/to/plan.md]'
agent: 'agent'
tools:
  - execute
  - read
  - search
  - edit
  - codebase
---

# Execute Plan

Use this prompt after a plan is already approved and ready to implement.

Follow the skills:

- `.github/skills/repo-delivery/SKILL.md`
- `.github/skills/execution-environment/SKILL.md`

## Copilot-native usage

- Use built-in `/plan` first if the work is not already planned.
- Follow the plan literally unless the user explicitly authorizes a deviation.
- Stop cleanly on blockers instead of skipping ahead.
