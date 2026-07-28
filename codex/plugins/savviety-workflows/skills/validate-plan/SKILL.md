---
name: validate-plan
description: "Validate an implementation plan before execution. Checks markdown structure, discrete tasks, acceptance criteria, placeholders, closed decisions, and parallel execution shape."
---

# Validate Plan

Use this before executing a written implementation plan.

## Workflow

1. Resolve the plan path from the user argument. If omitted, use the newest `*.md` under `docs/plans/`.
2. Run `python3 <skill-root>/scripts/validate_plan.py <path>`.
3. Report all failures together with line references where available.
4. Do not execute or rewrite the plan unless the user asks for fixes.

## Validation Scope

The validator is a lightweight readiness gate. It catches mechanical issues that make execution unreliable:

- missing H1 title
- no discrete tasks
- prose-only or missing acceptance criteria
- explicit milestones with orphan tasks
- forbidden placeholders
- ambiguous task openers
- malformed closed decisions
- malformed `## Parallel Execution` sections

For the detailed standard, read `references/plan-readiness.md`.
