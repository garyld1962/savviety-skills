---
description: >-
  Specialist database schema and migration compliance pass grounded in the
  project's actual ORM, migration style, and schema conventions.
argument-hint: '[files or scope to review]'
agent: 'agent'
tools:
  - read
  - search
  - codebase
---

# Review DB

Use this prompt when built-in `/review` is too broad and you want a targeted
database compliance pass.

Follow the skills:

- `.github/skills/review-foundations/SKILL.md`
- `.github/skills/db-schema-review/SKILL.md`

## Copilot-native usage

- Detect the ORM and existing schema conventions before rendering findings.
- Emphasize migration safety and high-signal schema risks.
