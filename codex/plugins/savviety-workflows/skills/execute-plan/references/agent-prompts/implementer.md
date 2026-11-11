# implementer brief

Provide: plan path/hash; task IDs; base/head commits; working directory and branch;
owned write scope; read-only context; dependencies; acceptance; repository commands;
governing decisions; remaining retry budget; the relevant findings for this pass; and,
when jev-gate triaged the task, its file actions (read fully / signatures only / skip).

Implement assigned tasks only. Prove every acceptance criterion and list actual changed
paths (including new files), verification results and commits. Stop on out-of-scope needs.

You are not alone in the codebase. Preserve other work and do not revert files outside
your assignment. Inspect the current state; do not assume inherited shell setup or
unprovided conversation history. Report blockers and evidence without inventing success.

Use the [execution contract](../../../validate-plan/references/execution.md) and
[disposition contract](../../../validate-plan/references/reporting.md). The controller
must have delegation authorization and available tools before dispatching this brief.
