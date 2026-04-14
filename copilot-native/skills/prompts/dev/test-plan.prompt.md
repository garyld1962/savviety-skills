---
description: >-
  Create or refresh a TDD-first test plan that matches the repo's real test
  framework, file conventions, and source contracts.
argument-hint: '--task="<description>" | --validate | --refresh'
agent: 'agent'
tools:
  - read
  - search
  - execute
  - edit
  - codebase
---

# Test Plan

Use this prompt when the team wants tests to define the contract before or
alongside implementation.

Follow the skill: `.github/skills/test-planning/SKILL.md`

## Copilot-native usage

- Use built-in `/plan` for broader implementation planning.
- Keep test planning behavior-focused and tied to actual code signatures.
