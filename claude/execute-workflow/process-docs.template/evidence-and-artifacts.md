# Evidence and Artifact Standards

This document defines the evidence quality bar and artifact conventions for this project's governed workflow.

## Evidence Quality

### What counts as evidence

- File path and line range showing the behavior
- Test output proving pass or fail
- Command output showing build/lint/typecheck result
- Reproduction steps for a reported issue
- Before/after comparison for a change

### What does NOT count as evidence

- "I believe this could be a problem" without code reference
- Style preferences without functional impact
- Speculative requirements not in the original artifact
- Severity inflation without concrete harm description

## Proof Accounting

Code review should classify major behavioral areas as:

| Classification | Meaning |
|---|---|
| `proved` | Tests cover the behavior AND tests pass |
| `partially proved` | Some coverage exists but gaps remain |
| `unproved` | No test coverage or verification for this area |

Green tests do not imply stronger proof than the evidence supports. A passing test suite with low coverage is `partially proved`, not `proved`.

## Artifact Conventions

### File naming

All run artifacts live in the run folder: `<runs_root>/yyyy-mm-dd-HHMMSS/`

Use the canonical template names:
- `execution-report.md`
- `review-plan.md`
- `review-code.md`
- `adversarial-review.md`
- `disposition-log.md`
- `postmortem.md`

### Content rules

- Keep artifacts concise
- Use repo-relative paths (not absolute)
- Write `None` in required sections with no content
- Do not restate the requirements artifact — reference it
- Link between artifacts using relative paths within the run folder

### Artifact lifecycle

| Artifact | Created during | Updated during |
|---|---|---|
| execution-report | Closeout | Reconciliation |
| review-plan | Planning review | — |
| review-code | Code review | Disposition loop |
| adversarial-review | Adversarial pass | Disposition loop |
| disposition-log | First finding raised | Every disposition round |
| postmortem | Postmortem phase | — |
