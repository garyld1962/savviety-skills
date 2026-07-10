# Execute Plan Task Loop

Use this reference for the per-task execution rhythm.

## For Each Task

1. Read the task requirements, acceptance criteria, target files, and verification command.
2. Inspect the existing code before editing.
3. Implement the smallest coherent slice that satisfies the task.
4. Run the task-specific verification command.
5. Fix failures within the retry budget.
6. Commit only when the task is complete, verified, and the user requested or workflow requires commits.
7. Update the execution log with files changed, verification results, and deviations.

## Ambiguity Handling

Ask the user only when the answer cannot be discovered from repo context and a wrong assumption would risk correctness, data loss, security, or public API behavior.

Proceed without asking for:

- Naming that follows existing patterns.
- Mechanical placement matching nearby code.
- Test fixture shape copied from established tests.
- Minor implementation details already implied by the plan.

Abort in autonomous or batch contexts when a blocking ambiguity remains.

## Decision Records

Write a decision record only when a future maintainer or agent could plausibly reverse the choice.

Good triggers:

- Multiple valid designs with different tradeoffs.
- A plan deviation needed to preserve correctness.
- A cross-module contract decision.
- A risk accepted by the user.

Avoid records for forced choices, tiny local edits, and direct plan instructions.

## Retry Budget

Track retries globally across implementation, verification, review fixes, and merge conflicts.

Default budget: 8 retries.

Increment the counter after each failed fix attempt, failed verification rerun, failed review fix, or failed merge repair. When exhausted, stop, preserve work, and report the blocker.

The loop fuse in `references/loop-fuse.md` overrides this budget. If the fuse trips, stop immediately even when retry budget remains.

## Verification Reruns

Before a verification rerun:

1. Record the failure signature.
2. State the one new piece of evidence or one concrete fix that justifies the rerun.
3. Run only the narrowest command that can prove the fix.

Do not rerun broad acceptance, restart dev servers, change ports, or switch tools when the previous failure was caused by a malformed verification command. Fix the verification command and rerun that single check.
