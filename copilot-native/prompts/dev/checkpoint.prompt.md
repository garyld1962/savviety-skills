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
- Use built-in `/review` separately for the quick/default review path.
- Use `prompts/review/code-review.prompt.md` when a deeper defect-focused review is needed.
- Use `prompts/review/professional-review.prompt.md` when the implementation also needs a senior engineering-judgment pass.
