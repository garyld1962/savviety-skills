---
name: validate-plan
description: "Validate a task graph plan's YAML, dependencies, write ownership and acceptance before execution, then review semantic readiness. Use for plan checks; do not execute or rewrite the plan unless requested."
---

# Validate plan

Read [the plan contract](references/plan-format.md). The bundled scripts require
Python 3 and PyYAML; missing dependencies are a reported blocker.

1. Resolve the explicit plan path. If omitted, inspect execution-plan candidates in
   docs/plans and choose only an unambiguous match; do not pick a PRD by modification time.
2. Run `python3 <this-skill>/scripts/validate_plan.py <plan.md>`.
   Use --json for parsed task metadata, diagnostics and the exact-byte plan hash.
3. Review what the script cannot prove: observable/relevant acceptance, repo command
   validity, actual file ownership, requirement coverage, consistent closed decisions,
   referenced decision records and unresolved product choices.
4. Return PASS only when both structural and semantic checks pass. Distinguish
   structural success from readiness. Return all failures with task IDs and remedies.
5. When called from an authorized planning/execution workflow, repair scoped issues
   and revalidate; when asked only for review, return findings without changing files.

The [execution](references/execution.md), [requirements](references/prd-planning.md)
and [reporting](references/reporting.md) references provide the shared downstream
contract. Before a final execution success claim run
`python3 <this-skill>/scripts/validate_report.py <report.json> --plan <plan.md>`.

## Examples
- Two independent tasks own the same lockfile → FAIL; assign an owner and dependency.
- A syntactically valid plan says "the feature works" → semantic FAIL; require proof.

## Closed decisions and open decisions
Validate the supplied decisions for conflicts and source authority. Do not reopen them
merely because another design is possible.

## Do not
Do not run acceptance commands during a read-only validation, equate script exit 0
with complete readiness, or schedule a malformed dependency graph with --force.

## Copilot integration
Use available Copilot tools and repository instructions. This durable skill works
without prompt-file discovery; the matching prompt is an optional VS Code shortcut.
Do not require /fleet, /tasks or any other host-specific command when it is unavailable.
