---
description: >-
  Senior-bar engineering review. Use when the code may work but you need to
  know whether the design and implementation choices are professional-grade for
  realistic scale, failure, operations, and maintenance.
argument-hint: '[files, commits, or scope to review]'
agent: 'agent'
tools:
  - read
  - search
  - changes
  - codebase
---

# Professional Review

Use this prompt when the question is:

> "Even if this works, were the right engineering choices made?"

This review exists to catch amateur-but-functional solutions: `File.ReadAllText`
on huge inputs, in-memory aggregation that explodes at scale, retry patterns
that look plausible but collapse under load, or architectures that will become
operational pain.

Prefer built-in `/review` for the quick/default path. Use this prompt when you
want an explicit senior-engineering judgment pass.

## Workflow

1. Read `.github/copilot-instructions.md` first.
2. Follow the shared review engine: `.github/skills/review-engine/SKILL.md`
3. Load and apply the **professional-review-rubric** skill
   (`copilot/skills/professional-review-rubric/SKILL.md`) for all craft
   grading. That skill is the authoritative source for:
   - the 4 seniority grades (`junior`, `mid`, `senior`, `staff`)
   - all 7 axis definitions (Clarity, Judgment, Forethought, Idiom,
     Testability, Scope discipline, Abstraction)
   - citation requirements and split-decision rules
4. Default to `profile: professional-default`.
   - Use `professional-pre-production` before releases or on high-blast-radius changes.
5. Review the actual changed scope from the `changes` tool unless the user
   explicitly names files, commits, or directories.
6. Keep this prompt focused on engineering choice quality:
   - realistic performance and memory behavior
   - resilience and failure-mode quality
   - concurrency and lifecycle correctness under pressure
   - operability and debuggability
   - maintainability and architecture fit
   - requirements fit and dependency judgment
7. Cite concrete failure or scale scenarios, not vague "best practice" claims.
8. Emit a merged report titled `Professional Review`.

## Positioning

- Built-in `/review` = quick/default
- `domain-review` = direct implementation defects
- `professional-review` = professional-grade engineering judgment

## Hard rules

- Do not reduce this to style commentary.
- Do not praise or criticize decisions without a concrete engineering reason.
- Do not use "works today" as evidence that the choice is professional.
