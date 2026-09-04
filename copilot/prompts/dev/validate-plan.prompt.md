---
name: validate-plan
description: "Validate a task graph plan's YAML, dependencies, write ownership and acceptance before execution, then review semantic readiness. Use for plan checks; do not execute or rewrite the plan unless requested."
argument-hint: "Provide a source or plan path and any workflow options."
agent: agent
---

Follow the [validate-plan skill](../../skills/validate-plan/SKILL.md) for the full workflow.
Preserve all user arguments, source requirements and authorization. Read its linked
contracts before acting and return verified artifacts or concrete blockers.
