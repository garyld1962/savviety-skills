# Execute PRD Workflow

Use this to convert a PRD, story, work item, or rough requirement into an executable plan.

## Flow

1. Load the repo contract from `AGENTS.md` or the repo's established instruction file.
2. Load the requirement source from a file, direct prompt, issue, or work item.
3. Classify the plan type: feature, bug, migration, refactor, operations, or research.
4. Audit current state before proposing work.
5. Run `prd-validate` when ambiguity blocks execution.
6. Extract non-negotiables: acceptance criteria, scope limits, user-visible behavior, data constraints, compatibility, and test obligations.
7. Draft the plan with tasks, verification, risks, rollback notes, and acceptance criteria.
8. Run `parallel-optimization` only when independent lanes are plausible.
9. Run `validate-plan`.
10. Execute only after the user confirms the plan or clearly requested autonomous execution.

## Plan Minimum Structure

- Goal and source requirement.
- Current-state findings.
- Non-goals.
- Task list with owners or write scopes.
- Acceptance criteria.
- Verification commands.
- Risks and rollback.
- Parallel execution metadata when applicable.

## Boundary

Do not skip from vague requirements to implementation. If the plan cannot be validated, stop at the plan and surface the blockers.

