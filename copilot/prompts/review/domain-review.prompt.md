---
description: >-
  Structured defect-focused review. Use when built-in /review is too broad or
  too shallow and you want an evidence-based pass for correctness, tests,
  async, API contract, data integrity, and direct implementation mistakes.
argument-hint: '[files, commits, or scope to review]'
agent: 'agent'
tools:
  - read
  - search
  - changes
  - codebase
---

# Code Review

Use this prompt when the question is:

> "What is concretely wrong, risky, missing, or incorrectly implemented in this code?"

Prefer built-in `/review` for the quick/default path. Use this prompt when you
need a deeper, structured review with explicit domain selection and a merged
report.

## Workflow

1. Read `.github/copilot-instructions.md` first.
2. Follow the shared review engine: `.github/skills/review-engine/SKILL.md`
3. Default to `profile: code-default`.
   - Use `code-comprehensive` for larger or more consequential changes.
4. Review the actual changed scope from the `changes` tool unless the user
   explicitly names files, commits, or directories.
5. Keep this prompt defect-focused:
   - correctness bugs
   - missing or weak tests
   - missing `async` / bad async behavior
   - API and validation mistakes
   - data-integrity risks
   - concrete security defects
6. Do **not** drift into generic "best practices" or taste-based advice.
7. Emit a merged report titled `Code Review`.

## Positioning

- Built-in `/review` = quick/default
- `domain-review` = deeper evidence-based defect review
- `professional-review` = senior engineering judgment about whether the choices
  are professional-grade, even if the code "works"

## Hard rules

- Do not confuse direct defects with broader engineering-choice critique.
- Do not skip the selected-domains section.
- Do not report style-only issues.
