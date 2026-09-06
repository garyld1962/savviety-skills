---
name: validate-plan
description: Check plan structure, ownership and readiness to execute.
---

# Validate plan

## When to Use

Use `/validate-plan <path>` for an existing execution plan, or as the check
inside an authorized PRD/plan workflow.

## Procedure

Read [Hermes execution setup](references/hermes.md) and
[the plan contract](references/plan-format.md). Resolve one explicit plan or
an unambiguous execution plan under `docs/plans/`; do not pick a PRD by date.

Run the bundled `scripts/validate_plan.py <plan.md>` with Python 3 and PyYAML
in the repository's execution environment. `--json` includes diagnostics,
parsed task metadata and the exact-byte plan hash. Use the setup reference
to locate scripts and dependencies.

Review what the script cannot prove: observable acceptance, actual ownership,
valid repository commands, requirement coverage, source authority, consistent
closed decisions and unresolved product choices. In a review-only request,
return findings without editing files or running acceptance commands. Repair
and revalidate when part of already authorized planning or implementation.

## Pitfalls

Script exit 0 proves structure only. Do not reopen settled decisions merely
because another design is possible. Malformed or cyclic graphs cannot be
executed with a force option. Missing dependencies are an unavailable check.

## Verification

Report readiness only after structural and semantic checks pass. Explain
failures and remedies using [simplify](../simplify/SKILL.md).
For final execution proof, use [reporting](references/reporting.md) and run
`scripts/validate_report.py <report.json> --plan <plan.md>` before claiming
success. The [execution](references/execution.md) and
[requirements](references/prd-planning.md) references govern those workflows.
