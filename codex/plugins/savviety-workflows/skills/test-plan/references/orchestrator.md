# Test Plan Orchestrator

Use this reference for TDD-first test planning.

## Modes

- `plan`: create a plan from a task or requirements.
- `validate`: run generated tests and update plan status.
- `refresh`: update the plan after requirements or implementation changed.

## Discovery

Read only the context needed for the target:

- Repo instructions such as `AGENTS.md` or legacy `CLAUDE.md`.
- Workspace package config.
- `.test-plan/config.json` if present.
- Validation schemas, DB schema, status enums, reference implementation, and existing tests for the target layer.
- `references/dependency-classification.md` for dependency testing strategy.

## Analyst Selection

- Service: contract compliance, boundary validation, integration surface, and state lifecycle when a status field exists.
- Router/API: contract compliance, boundary validation, integration surface.
- Schema: contract compliance and boundary validation.
- Component: contract compliance, boundary validation, integration surface.

Analyst references live in `references/analysts/`.

## Consolidation

1. Deduplicate equivalent specs by behavior and target test file.
2. Keep the higher priority spec. If priorities match, keep the stronger assertion set.
3. Group specs by test file.
4. Apply the priority rubric from `references/foundations/priority-rubric.md`.
5. Write the plan schema from `references/foundations/plan-schema.md`.

## Output

Always include:

- Plan verdict: `READY`, `PARTIAL`, or `BLOCKED`.
- Analyst list.
- Spec counts by priority.
- Generated or expected test files.
- Plan path.
- Report path when a report is written.

Write tests only when the user asks or the invoking workflow requires generated stubs.

