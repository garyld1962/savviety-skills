---
description: >-
  Audit dependency health across security, outdated packages, unused
  dependencies, and licenses using the repo's real ecosystem and tooling.
argument-hint: '[--security-only] [--check outdated|unused|licenses] [--fix]'
agent: 'agent'
tools:
  - read
  - search
  - execute
---

# Dependency Audit

Use this prompt for supply-chain hygiene, release readiness, or CVE response.

Follow the skill: `.github/skills/dependency-change-management/SKILL.md`

## Copilot-native usage

- Detect the ecosystem before selecting any audit command.
- Distinguish direct vs transitive issues and real unused dependencies vs build
  tooling.
