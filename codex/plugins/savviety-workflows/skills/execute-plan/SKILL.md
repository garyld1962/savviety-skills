---
name: execute-plan
description: "Execute or resume a written task graph plan with ownership checks, acceptance proof, milestone reviews, bounded retries and final-head gates. Use for an existing plan; use execute-prd when requirements still need planning."
---

# Execute plan

Read the sibling validate-plan skill's [execution contract](../validate-plan/references/execution.md),
[plan format](../validate-plan/references/plan-format.md), and
[reporting contract](../validate-plan/references/reporting.md) before implementation.

1. Resolve the plan, command contract and existing work. Validate structure and
   semantic readiness, record plan/base hashes, and prepare a working branch.
2. Execute ready tasks in dependency order. Use concurrent workers only with existing
   authorization and actual host support; otherwise run the same graph sequentially.
3. Check ownership against actual changed paths, prove each acceptance criterion,
   and review at milestone boundaries. Preserve governing decisions.
4. Apply global retry/fix/time budgets and the loop fuse. A missing review, unproved
   acceptance or false alignment blocks completion.
5. Complete required gates on the final code commit, disposition every finding, and
   validate the canonical report using validate-plan's scripts/validate_report.py.
   Preserve work and write reports/postmortems on failure as well as success.

## Options and compatibility
Honor explicit --resume, --create-branch, --interactive=yes|no|auto,
--max-retries=N, --max-fix-cycles=N, --max-minutes=N,
--adversarial=auto|always|never, --accept-risk=<finding-id>,
--run-folder=<path|auto|off>, and --postmortem=auto|always|never.
With run-folder=off, return the same report content without persistent run files.
With postmortem=never, still include blockers and recovery evidence in the report.
Accept --postmortem-mode=auto|full|lightweight to control detail, not required evidence.
A force request must identify waived validation findings; it never makes an invalid
dependency graph executable. Reject unknown options instead of silently ignoring them.
Options are instructions to the agent, not a claim that a background CLI exists.

## Examples
- "Execute docs/plans/export.md" → validate, implement, verify and report.
- "Resume this failed plan" → reconcile saved hashes, commits and proof before continuing.

## Closed decisions and open decisions
Honor the plan and referenced decisions. Resolve material codebase ambiguity from code
first, then ask or report a batch blocker. Do not reopen choices already settled.

## Do not
Do not treat worker status as proof, missing findings as a clean review, or a graph as
permission to delegate. Do not bypass a required gate to achieve a successful verdict.

## Codex integration
Use $execute-plan and native Codex tools. Read AGENTS.md; preserve current host permissions.
Private agent briefs live under execute-plan/references/agent-prompts. Legacy references
are archival and are not part of the active contract.
