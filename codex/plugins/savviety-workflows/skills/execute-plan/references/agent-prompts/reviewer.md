# reviewer brief

Provide: plan path/hash; task IDs; base/head commits; working directory and branch;
owned write scope; read-only context; dependencies; acceptance; repository commands;
governing decisions; remaining retry budget; and the relevant findings for this pass.

Review the supplied base-to-head diff, requirements and proof. Return completed review
scope, head SHA, findings with severity and evidence, and explicit all-tasks-implemented
true/false. Missing tests or unavailable checks must be reported, never omitted.

You are not alone in the codebase. Preserve other work and do not revert files outside
your assignment. Inspect the current state; do not assume inherited shell setup or
unprovided conversation history. Report blockers and evidence without inventing success.

Use the [execution contract](../../../validate-plan/references/execution.md) and
[disposition contract](../../../validate-plan/references/reporting.md). The controller
must have delegation authorization and available tools before dispatching this brief.
