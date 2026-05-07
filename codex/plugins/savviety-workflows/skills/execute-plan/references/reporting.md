# Execute Plan Reporting

Use this reference for the final execution report.

## Markdown Sections

- `Summary`: plan path, base SHA, final SHA, branch, verdict.
- `Per-Task Summary`: task, status, files changed, verification, commit if applicable.
- `Milestones`: verification commands, review results, accepted risks.
- `PR Reviews`: checkpoint, code review, professional review, adversarial review.
- `Plan Deviations`: what changed, why, and whether the user approved it.
- `Open Questions`: only unresolved questions that affect follow-up work.
- `Verdict`: `PASS`, `WARN`, or `FAIL`.

## Verdicts

- `PASS`: all required tasks, verification, and review gates passed.
- `WARN`: the work is complete, but non-blocking risks, skipped optional gates, or environment limitations remain.
- `FAIL`: required work, verification, or review gates failed.

## Run Folder

If the repo declares a run artifact folder, write:

- `execution-report.md`
- `execution-report.json`
- `disposition-log.md`
- `postmortem.md` when triggered

Otherwise, keep the report in the location requested by the user or plan.

## Postmortem Trigger

Create a postmortem when the run ends in `WARN` or `FAIL`, exhausts retry budget, escalates to the user, or exposes a workflow defect.

If `references/loop-fuse.md` trips, include the failure signature, retry count, commands attempted, and the single recommended next action.
