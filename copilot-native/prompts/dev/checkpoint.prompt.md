---
description: >-
  Run a repo-specific quality gate across the changed scope by detecting the
  real lint, build, and test commands before execution.
argument-hint: '[optional scope]'
agent: 'agent'
tools:
  - execute
  - read
  - search
---

# Checkpoint

Use this prompt for a fast quality gate before pushing, merging, or shipping.

Follow the skills:

- `.github/skills/repo-delivery/SKILL.md`
- `.github/skills/execution-environment/SKILL.md`

## Copilot-native usage

- Prefer configured repo commands over invented ones.
- Report PASS, FAIL, and SKIP with enough evidence to act.
- Use built-in `/review` separately when a code review is also needed.
