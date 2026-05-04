# Postmortem Workflow

This document defines when and how to run a postmortem after a governed execution run. Edit trigger thresholds and focus areas to match your project.

## When to Run a Postmortem

Run a postmortem after any governed execution run that:
- Resulted in `blocked` or `awaiting-human-decision`
- Resulted in `completed-with-accepted-risk`
- Took more than the expected review rounds (escalation threshold exceeded)
- Surfaced findings that indicate a process gap (not just a code bug)

Optional: run a lightweight postmortem after any `completed` run to capture process improvements.

## Postmortem Inputs

The postmortem reads these artifacts from the run folder:
- `execution-report.md` — what was done, final gate state
- `review-code.md` — findings and proof accounting
- `adversarial-review.md` — challenge findings
- `disposition-log.md` — resolution history
- The original requirements artifact (AERS/PRD)

## Postmortem Focus Areas

The postmortem should analyze:

1. **Workflow execution** — Did each phase add value? Were any phases skipped inappropriately?
2. **Review quality** — Were findings evidence-based? Were any findings missed?
3. **Disposition effectiveness** — Did the loop converge? Were escalations justified?
4. **Tool and skill usage** — Were the right tools used? Any tool misuse or gaps?
5. **Requirements fit** — Was the AERS/PRD clear enough? Did ambiguity cause rework?
6. **Process gaps** — What did the process NOT catch that it should have?

## Output

Write `postmortem.md` in the run folder using the postmortem template.

The postmortem should make it easy for a senior developer to understand:
- what happened
- what worked
- what broke down
- what the process missed
- what should change next

## What a Postmortem is NOT

- NOT a second requirements document
- NOT a chat transcript summary
- NOT a restatement of review findings without process context
- NOT a blame document
