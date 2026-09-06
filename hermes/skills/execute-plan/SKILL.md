---
name: execute-plan
description: Execute or resume a plan with checks and clear progress.
---

# Execute plan

## When to Use

Use `/execute-plan <path>` to implement or resume an existing written plan.
Use execute-prd when requirements still need planning.

## Procedure

Before the first update, read [simplify](../simplify/SKILL.md),
[Hermes execution setup](../validate-plan/references/hermes.md),
[execution](../validate-plan/references/execution.md),
[plan format](../validate-plan/references/plan-format.md), and
[reporting](../validate-plan/references/reporting.md).

1. Resolve the plan and project commands; inspect existing work. Use
   [validate-plan](../validate-plan/SKILL.md), record plan/base hashes, and
   prepare the working branch. Reconcile saved evidence when resuming.
2. Implement ready tasks in dependency order, checking actual changed paths
   against ownership. Default to sequential execution. Delegation requires
   both existing authorization and available Hermes tools.
3. Prove every acceptance criterion and review at milestones. Run the declared
   repository checks and review the diff locally when a separate reviewer is
   unavailable; report honestly that it was the same agent. If policy requires
   an independent reviewer, its absence remains a blocker. Apply the shared
   professional/adversarial review requirements; this pilot has no separate
   review skill packages, so perform those reviews explicitly with available
   tools and retain their scope, findings and evidence.
4. Follow shared retry/time limits, record every finding's outcome, verify
   requirement coverage and validate the canonical execution report. Preserve
   work and recovery context on failure. Apply simplify to every user update.

Honor `--resume`, `--create-branch`, `--interactive=yes|no|auto`,
`--max-retries=N`, `--max-fix-cycles=N`, `--max-minutes=N`,
`--adversarial=auto|always|never`, `--accept-risk=<finding-id>`,
`--run-folder=<path|auto|off>`, `--postmortem=auto|always|never`, and
`--postmortem-mode=auto|full|lightweight`. These are instructions to the agent,
not executable CLI flags. With run-folder=off, return the report content in
the conversation. With postmortem=never, still retain blockers and recovery
evidence. Reject unknown options. A force request must identify waived
semantic findings; it cannot make an invalid graph executable.

## Pitfalls

Do not call Claude's Workflow runtime or claim that it ran. A passed check,
completed task, committed change and deployment are different outcomes.
Preserve existing user edits and permission settings. Updating Linear,
publishing a PR, merging or deploying follows the user's authorization.

## Verification

Completion requires every task proved and every required check/review against
the final code commit, plus a valid report. If commits are prohibited, return
a draft verification summary identifying uncommitted work, as specified by
the shared reporting contract. Never label unavailable checks as passing.
