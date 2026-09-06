---
name: execute-prd
description: Turn requirements into a plan; build when requested.
---

# Execute PRD

## When to Use

Use `/execute-prd <file or requirement>` to plan or build a PRD, RFC, story,
or Linear issue. Use execute-plan for an existing implementation plan.

## Procedure

Before the first update, read [simplify](../simplify/SKILL.md),
[Hermes execution setup](../validate-plan/references/hermes.md),
[requirements planning](../validate-plan/references/prd-planning.md), and
[the plan format](../validate-plan/references/plan-format.md).

Resolve one source, read project instructions and discover declared commands.
Audit existing code and tests, assess requirements readiness, then write the
task graph with dependencies, file ownership, acceptance proof and milestone
boundaries. Preserve requirement IDs and closed decisions. For a material
unresolved design, compare alternatives locally using the shared planning
criteria; this pilot does not require a separate design-twice skill.

Use [validate-plan](../validate-plan/SKILL.md) for structural and semantic
checks; repair at most three times. If building was requested, continue with
[execute-plan](../execute-plan/SKILL.md) after validation. A planning-only
request ends with the plan. Existing implementation authorization is enough.

Accept one file, direct requirement, issue URL, or `--linear <issue>` source.
Use an available connected Linear integration; otherwise ask for the issue
content. Preserve Linear as the tracker; do not introduce a second backlog.
Fetching context does not authorize posting updates or changing issue status.

Honor `--type=bug|feature|refactor|infra`, `--plan-path=<path>`,
`--parallel=auto|sequential`, and `--design-it-twice=auto|always|never`
(alias `--design-twice`). Forward execution options to execute-plan;
report unsupported options instead of silently ignoring them.

## Pitfalls

Do not assume greenfield, invent missing product decisions or integrations,
or treat shell TTY state as proof of human presence. In unattended execution,
stop with concrete missing information when a material decision is unresolved.
Apply simplify to every assistant-written update through planning and execution.

## Verification

The plan covers the source requirements, passes both forms of validation,
and identifies remaining uncertainty. A request to build continues through
implementation and evidence; a valid plan alone does not mean work is done.
