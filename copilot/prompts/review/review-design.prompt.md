---
description: >-
  Targeted UI review that uses the shared review engine with design-system and
  accessibility focus against the project's real conventions.
argument-hint: '[files or scope to review]'
agent: 'agent'
tools:
  - read
  - search
  - codebase
---

# Review Design

Use this prompt when built-in `/review` is too broad and you want a targeted UI
design-system and accessibility pass.

Follow the skills:

- `.github/skills/review-engine/SKILL.md`
- `.github/skills/ui-design-compliance/SKILL.md`

## Routing

- Start from the `domain-review` lane and emphasize `ui-design` concerns plus the
  local design-system rules from `ui-design-compliance`.
- Escalate to `professional-review` only when the issue is architectural or
  lifecycle-related rather than a direct UI defect.

## Copilot-native usage

- Detect the actual design system and tokens before reviewing.
- Focus on local conventions plus accessibility, not taste-based feedback.
