# Requirements to a validated plan

1. Read the repository instruction file and its Commands contract (`lint`,
   `build`, `test`, `default_branch`, `package_manager`). Missing commands halt
   execution; show the missing fields without inventing commands.
2. Resolve exactly one source: explicit file, GitHub issue, `--ado`, or
   `--linear`. Prefer an available connected service; never pretend a missing
   integration exists. The work-item reader returns content; this caller saves
   the canonical snapshot at `docs/plans/PRD-<slug>.md` with source URL/ID.
   Without an explicit source, inspect `prompt.md`, `docs/plans/PRD.md`,
   `PRD.md`, then relevant specs in `docs/`. If more than one is plausible,
   ask which is authoritative; in a noninteractive run report `plan-ambiguity`.
3. Audit code, contracts, existing behavior and tests before planning. Classify
   the dominant type as `bug`, `feature`, `refactor`, or `infra`.
4. Apply the readiness rubric below using the audit. Keep the numeric score
   and gap list; an interactive requirements interview is a separate remedy.
5. Extract requirement IDs, MUST/SHOULD statements, forbidden behavior,
   compatibility, verification and reporting obligations. Map each to tasks
   and final proof. Preserve closed decisions and their authority.
6. For significant unresolved architecture in feature/refactor work, use the
   design-twice workflow: compare minimal surface, flexibility and common-case
   interfaces. Honor existing delegation authorization; otherwise compare
   locally. Record the chosen design and rejected alternatives. Do not reopen
   settled architecture or guess a material product decision in batch mode.
7. Write `docs/plans/execute-plan-<slug>.md` (or the requested path) using the
   task graph contract. Shape tasks by type:
   - bug: reproduce, minimal fix, regression proof;
   - feature: contracts, behavior tests, implementation, integration;
   - refactor: characterize existing behavior, small transformations, verify;
   - infra: configuration, authorized environment checks, smoke proof, rollback.
   Include final repository verification and requirement traceability. Derive
   dependencies and ownership from actual shared surfaces. Optimization changes
   scheduling, never requirements. A sequential request adds ordering edges.
8. Run structural validation, then review acceptance, existing-state fit,
   closed decisions and requirement coverage. Repair at most three times;
   stop with remaining blockers if the plan still fails.
9. If the user requested implementation, hand off to execute-plan once the
   gates pass. A request only to plan ends with the plan. Do not add another
   approval round to an already authorized build request. The validated plan
   becomes execution authority; retain the source for traceability.

## Automated readiness rubric

Score these sections: Problem Summary; Scope; Functional Requirements;
Closed Decisions; Open Decisions; Public API / Interface; Data Models;
Verification Matrix / Test Strategy; Repo Starting State; Tooling Assumptions;
Execution Preflight; Definition of Done; Readiness Assessment.

Each substantive section scores 0, a stub scores 1, a missing section scores 2.
A specific explanation that a section is inapplicable counts as substantive.
Add 2 for each unresolved high-risk ambiguity: problem, actor, scope,
destructive behavior, source of truth, permissions, calculation/normalization,
or implementation-changing stack choice.

| Score | Readiness | Action |
|---|---|---|
| 0–2 | Ready | Proceed; note any gap. |
| 3–6 | Partially ready | Ask only material open questions when interactive; in batch mode record nonblocking gaps as risks. |
| 7+ | Not ready | Stop planning with `requirements-incomplete` and the scored gaps; suggest a focused prd-validate interview. |

A numeric score does not authorize guessing a blocking product, security or
data decision. Such a decision still blocks even if the total is below 7.
Never auto-start a human interview in a noninteractive run. Use session context
to determine interactivity; a chat tool's shell TTY is not a human-presence test.
