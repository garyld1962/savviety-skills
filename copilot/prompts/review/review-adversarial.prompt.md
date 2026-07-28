---
description: >-
  Built-in-first cross-model code review. Use `/model` first, then run this
  prompt to challenge changed code through skeptic, architect, and minimalist
  lenses and write a persisted report.
argument-hint: '[files, commits, or scope to review]'
agent: 'agent'
tools:
  - read
  - search
  - changes
  - codebase
  - edit
---

# Adversarial Review

Use this prompt when built-in `/review` is not enough and you want a deliberate
second-opinion pass from a **different model**.

## Workflow

1. Confirm the active model is intentionally different from the one that wrote
   the code or earlier review output. If not, tell the user to run `/model`
   first, then continue.
2. Read `.github/copilot-instructions.md` before evaluating the code.
3. Follow the skill: `.github/skills/adversarial-review/SKILL.md`
4. Review only the actual changed scope from the `changes` tool unless the user
   explicitly names files or commits.
5. If there are no visible changes and no explicit scope, ask the user what to
   review instead of guessing.

## Positioning

- Prefer built-in `/review` for the default quick review path.
- Use this prompt when you want a stricter, cross-model challenge with explicit
  adversarial lenses and a persisted markdown report.
- This can challenge output from built-in `/review`, `domain-review`, or
  `professional-review`.
