---
description: >-
  Targeted database review that uses the shared review engine with schema,
  migration safety, query, and data-integrity focus grounded in project
  conventions.
argument-hint: '[files or scope to review]'
agent: 'agent'
tools:
  - read
  - search
  - codebase
---

# Review DB

Use this prompt when built-in `/review` is too broad and you want a targeted
database review pass.

Follow the skills:

- `.github/skills/review-engine/SKILL.md`
- `.github/skills/db-schema-review/SKILL.md`

## Routing

- Use `professional-review` when the main question is whether the schema,
  migration, indexing, or data-access choices are professional-grade.
- Use the `domain-review` lane when the main question is a direct defect in SQL,
  migration safety, transaction handling, or query behavior.
- In either case, anchor the findings in `db-schema-review`.

## Copilot-native usage

- Detect the ORM and existing schema conventions before rendering findings.
- Emphasize migration safety and high-signal schema risks.
