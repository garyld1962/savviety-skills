---
name: execute-prd
description: "Turn a PRD, RFC, prompt, story or ticket into an audited, readiness-scored task graph, validate it and implement when requested. Includes lightweight kickoff; use execute-plan for an existing execution plan."
---

# Execute PRD

Read the sibling validate-plan skill's [requirements workflow](../validate-plan/references/prd-planning.md)
and [plan contract](../validate-plan/references/plan-format.md).

1. Resolve one source and the repository command contract; audit current code and tests.
2. Apply the automated readiness score before planning. A requirements interview is
   offered for gaps, never silently launched in an unattended run.
3. Preserve requirement IDs, invariants and closed decisions. Use design-twice for
   material unresolved architecture in feature/refactor work.
4. Author tasks with depends_on, write_scope, milestone_end and mechanical acceptance.
   Preserve all requirements while optimizing dependencies and shared ownership.
5. Validate structure and semantic readiness, repairing at most three times.
6. If the user requested building, hand off to execute-plan after validation. If the
   request was only for a plan, return the plan. Existing implementation authorization
   is sufficient; do not add a confirmation round.

## Inputs and options
Accept a file/direct requirement or one --ado / --linear source; sources are mutually
exclusive. GitHub issue URLs are valid sources. Honor --type=bug|feature|refactor|infra,
--plan-path=<path>, --parallel=auto|sequential and
--design-it-twice=auto|always|never (also accept --design-twice).
Auto compares designs only for significant unresolved architecture. Never skips a
decision already settled. Forward recognized execution options to execute-plan;
flag unknown options rather than discarding them.

Lightweight kickoff uses the same audit, readiness and dependency contract at smaller
scope. Do not impose a large discovery interview on a clear, small build request.

## Examples
- "Build this PRD" → audit, score, plan, validate, then implement within the request.
- "Plan this feature but don't code" → stop with the validated plan and any open decisions.

## Closed decisions and open decisions
The source controls product scope. Once validated, the plan controls implementation;
source-to-plan mismatches are explicit ambiguities, not silent scope expansion.

## Do not
Do not assume greenfield, invent product decisions, require unsupported agent tools,
or create legacy wave/lane sections alongside the task graph.

## Codex integration
Use $execute-prd and native Codex tools. Read AGENTS.md; preserve current host permissions.
Private agent briefs live under execute-plan/references/agent-prompts. Legacy references
are archival and are not part of the active contract.
