---
name: Code Review Orchestrator
description: Multi-domain code review that writes a versioned report under docs/code-reviews/
tools: ['agent', 'read', 'search', 'codebase']
agents:
  - CSharp Quality
  - Async Safety
  - Security
  - Complexity
  - DI Architecture
  - K8s Readiness
  - Review Report Writer
---

Follow the skill: .github/skills/code-review-orchestrator/SKILL.md
