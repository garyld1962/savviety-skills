---
description: >-
  Design a repeatable evaluation suite for scoring AI-generated BA deliverables
  against professional quality criteria.
argument-hint: '[deliverables, org context, or quality concerns]'
agent: 'agent'
tools:
  - read
  - search
  - edit
---

# BA Eval Harness

Use this prompt to create a reusable scoring framework for BA deliverables that
AI helps draft.

Follow the skill: `.github/skills/ba-knowledge-ops/SKILL.md`

## Copilot-native usage

- Focus on observable pass/partial/fail criteria.
- Capture known AI-specific BA failure modes explicitly.
- Use the resulting harness to improve prompts and review future outputs.
