---
description: >-
  Build a reusable BA project context document that captures stakeholders,
  terminology, constraints, and AI working rules for later sessions.
argument-hint: '[project name or initiative]'
agent: 'agent'
tools:
  - read
  - search
  - edit
---

# BA Context Builder

Use this prompt when the recurring problem is missing project context rather
than missing implementation detail.

Follow the skill: `.github/skills/project-context/SKILL.md`

## Copilot-native usage

- Prefer concise, reusable context over long narrative prose.
- Treat the output as a reference artifact that can be reused through `@file`
  mentions in later Copilot CLI sessions.
