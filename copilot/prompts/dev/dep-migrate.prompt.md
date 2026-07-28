---
description: >-
  Analyze a major dependency or runtime upgrade and produce a repo-specific
  migration guide from official docs and actual code usage.
argument-hint: '<package> <from-version> <to-version> [--scope <path>] [--dry-run]'
agent: 'agent'
tools:
  - read
  - search
  - execute
  - codebase
---

# Migration Guide

Use this prompt when a major version change needs a codebase-specific migration
plan rather than a blind package bump.

Follow the skill: `.github/skills/dependency-change-management/SKILL.md`

## Copilot-native usage

- Use built-in `/research` first for official vendor docs when needed.
- Use built-in `/plan` after the migration path is accepted and ready to
  execute.
