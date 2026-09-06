# Native execution contract

Read `plan-format.md`, `reporting.md`, and the repository command contract.
Use native editing, shell, review and optional agent tools. This workflow has
no dependency on another platform's orchestration host or scripts.

Read [the simplify output guidance](../../simplify/references/output.md) before
the first user update. Apply it to every assistant-written progress message,
task/milestone summary, blocker, decision request, and final response throughout
execution and resume. Internal check names and report schemas remain evidence;
explain their effect on the user's goal in the console.

## Preflight and resume

- Resolve one explicit plan. If omitted, use a unique execution plan candidate
  under `docs/plans/`; do not select an unrelated PRD merely because it is newer.
- Validate structure and semantic readiness before editing. A human's explicit
  force request may waive named semantic findings; malformed/cyclic graphs and
  unknown dependencies still cannot be scheduled. Log any waiver as a risk.
- Read governing decisions and probe declared tools in the same environment
  used for execution. Do not replace failed checks with weaker checks silently.
- Record plan SHA-256, base commit, branch, required gates and initial user
  changes. Create a working branch for nontrivial work when on the default
  branch; this is part of the requested implementation, not a new approval gate.
- Resolve referent, existing-state and scope-boundary ambiguities from code
  first. Ask only if a material choice remains; in batch mode stop and record
  `plan-ambiguity`. Ordinary implementation uncertainty is not a blocker.
- Resume only if plan hash, base and task evidence match the saved run and
  referenced commits are ancestors of the current branch. Verify working tree
  state and the last completed boundary. A task footer alone proves no success.
  A changed plan requires revalidation and an explicit reconciliation of work.

## Scheduling and task loop

Default to sequential execution. Delegate only when the user or governing
instructions authorize it and the current host exposes the tools; authorization
already given in this session remains valid. A graph describes safe ordering,
not permission to create agents. Report the actual mode used.

Choose tasks whose dependencies have succeeded. Only dispatch disjoint scopes
together; cap concurrency at the available/requested budget. At a milestone,
finish the active group and review before starting another group. Include the
plan hash, objective, scope, read-only context, dependencies, acceptance,
governing decisions and a warning to preserve other work in each worker brief.

For each task:
1. Inspect current code and the requirement before editing.
2. Implement the scoped behavior. Add a failing regression/characterization test
   when behavior demands it; do not write tests that only restate prose edits.
3. Run each acceptance check and applicable declared build/test checks. Record
   command, exit code or observation, evidence location and verified commit.
4. Inspect actual changed paths, including new/untracked files, against ownership.
   Re-plan and revalidate before writing outside scope.
5. Commit a verified task when repository policy requires commits. Include
   `Task N from <plan>`, `Plan-SHA: <sha256>` and `Base-SHA: <commit>` trailers.
   Review-fix commits name the finding and never impersonate task completion.
6. Record completion only with proof; a worker saying `done` is not proof.

If isolated branches/worktrees are used, integrate in dependency order and
reverify affected acceptance after integration. Never resolve a conflict by
blindly favoring one branch. Preserve both changes and stop if meaning is unclear.

## Budgets and reviews

Defaults: 20 total retries, 3 fix cycles per blocking finding, 60 minutes.
Honor explicit user/repo overrides. Count implementation, verification, review
and integration repair failures in the same global budget. A rerun requires a
new observation or concrete fix. Repeated identical failures without new evidence
trip the loop fuse immediately; do not rotate tools/ports to evade the blocker.

At milestones run focused acceptance and review. At the final boundary:

1. Run declared checkpoint commands and required code review over base-to-head.
2. Run professional review when requested by the plan/repo. Run adversarial
   review when requested, or in auto mode for at least 200 changed lines or
   authentication, authorization, secrets, payments or destructive-data changes.
3. Check every planned task and source requirement against implementation and
   proof. The alignment result must explicitly say `all_tasks_implemented: true`.
4. Fix blockers within budget and independently recheck the specific finding.
   A fixer claiming `fixed` does not close it. A second local review is useful
   when delegation is unavailable; describe it honestly as the same agent.
5. Record all required gates against the final code commit. Any later code fix
   invalidates affected evidence: rerun affected acceptance, required root gates,
   and final alignment; obtain review of the resulting diff before reporting.

Missing, null, malformed, skipped or failed required review/check output blocks
success. Empty findings count as clean only in a completed review with scope,
head commit and evidence. Never reinterpret an unavailable reviewer as `[]`.

## Failure and delivery

Write the report on success, blocked runs and exhausted budgets. Preserve the
working tree, branch and last successful commit; never reset/clean/force-push or
delete user work to recover. Include a concrete next action and resume context.
Creating a PR follows the user's request and repository policy; merging or
deploying requires authorization for that action. Use available GitHub tools
after gh-readiness; retain complete artifacts when access is unavailable.
