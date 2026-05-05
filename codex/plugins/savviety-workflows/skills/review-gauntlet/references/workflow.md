# Review Gauntlet Workflow

Use this to review the quality of an existing code review.

## Inputs

- The review text.
- The reviewed diff or relevant source files.
- The stated intent of the change.

## Lenses

- Skeptic: Are findings accurate, line-cited, and supported by code?
- Architect: Did the review miss structural, boundary, or data-flow risks?
- Pragmatist: Are recommendations actionable and proportionate?

## Verdict

- `ACCEPT`: review is accurate and actionable.
- `AMEND`: review is mostly useful but needs corrections or missing findings.
- `REJECT`: review is misleading, unsupported, or misses blocking issues.

Lead with corrections to the review, then list missed findings and false positives.

