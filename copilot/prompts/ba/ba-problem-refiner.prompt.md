---
description: >-
  Refine a vague business problem into a precise, solution-neutral problem
  statement with explicit gaps, constraints, and success criteria.
argument-hint: '[rough problem statement, stakeholder ask, or source note]'
agent: 'agent'
tools:
  - read
  - search
  - edit
---

# BA Problem Refiner

Use this prompt when the problem statement is still vague enough that the team
could build the wrong thing.

Follow the skill: `.github/skills/prd-readiness/SKILL.md`

## Copilot-native usage

- Ask only the smallest set of questions needed to close high-risk ambiguity.
- Keep the output solution-neutral unless the user has already chosen an
  implementation direction.
- Use this before `#prompt:prd-validator` or built-in `/plan`, not instead of
  them.
