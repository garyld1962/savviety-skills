---
name: review-disposition-governance
description: Governance rules for plan review, code review, adversarial review, finding disposition, accepted-risk handling, and human arbitration in autonomous execution workflows.
---

# Review and Disposition Governance

Use this skill when the workflow includes:

- `review-plan.md`
- `review-code.md`
- `adversarial-review.md`
- `disposition-log.md`
- human arbitration
- accepted-risk decisions

## Core principle

> Green validation is not enough. Completion requires evidence-based review and explicit disposition of meaningful findings.

## Senior baseline principle

Use a minimum senior-developer baseline at high-leverage seams:

- public API shape
- module boundaries
- ownership of data and responsibilities
- validation and error handling
- observability and diagnosability
- extension points

Do not interpret this as a requirement to polish every line equally.

## Source of truth

Workflow and artifact structure are defined in:

- `.github/docs/process/execute-workflow.md`
- `.github/docs/process/review-and-disposition.md`
- `.github/docs/process/evidence-and-artifacts.md`
- `.github/docs/process/document-schema.md`
- `.github/docs/templates/*.template.md`

Do not invent a different report structure if a canonical template already exists.

If those shared process or template files are missing in the consuming repo,
stop and say the governed workflow support files are not installed. Name the
missing paths explicitly and do not invent substitute docs, templates, or
artifact schemas.

## Required review set

The canonical review set contains:

- `review-plan.md`
- `review-code.md`
- `adversarial-review.md`
- `disposition-log.md`

Use only the artifacts relevant to the run, but do not silently skip required gates defined by the workflow.

## Adversarial review independence

The adversarial review should be meaningfully independent from the main implementation path.

Preferred order:

1. use a different frontier model family
2. if unavailable, use a different model variant
3. in all cases, keep the adversarial role and evaluation criteria distinct

## Severity vocabulary

Use only these severity levels:

- `critical` — must be fixed; blocks completion if unresolved
- `major` — blocks completion if unresolved
- `minor` — does not block; surfaced for awareness
- `nit` — style or trivial; may be ignored

## Evidence standard

A meaningful finding must be evidence-based.

Include:

- severity (see severity vocabulary above)
- evidence (file:line references, specific diff lines)
- why it matters
- recommended fix

Do not drive the loop with:

- style-only commentary
- speculative requirements
- unsupported objections

## Elevation pass rule

After the code is green, run a short elevation pass.

The goal is to identify code that is correct but still below the desired senior baseline.

Only recommend elevation when it buys something concrete:

- lower future change cost
- reduced brittleness
- clearer ownership or boundaries
- better operability or debugging
- improved correctness margin
- measurable performance or memory improvement

Do not push rewrites for style-only reasons.

## Proof accounting rule

The code review should explicitly classify major behavioral areas as:

- `proved`
- `partially proved`
- `unproved`

Do not let green tests imply stronger proof than the evidence supports.

## Status vocabulary

Use only:

- `open`
- `fixed`
- `disagree-with-evidence`
- `defer`
- `accepted-risk`
- `resolved`

## Examples

- **Fixed finding:** A reviewer raises a high-signal issue in `review-code.md`,
  the coder fixes it, and the disposition log records the item as `fixed` with
  the updated evidence.
- **Accepted risk:** A real issue remains, a human explicitly approves
  proceeding anyway, and the disposition log records `accepted-risk` rather than
  pretending the finding was resolved.
- **Human arbitration:** Reviewer and coder still disagree after bounded review
  rounds, so the workflow escalates, records the human decision, and updates the
  final gate state accordingly.

## Disposition loop

### Step 1 — Reviewer raises findings

Reviewers write only high-signal findings in the appropriate review artifact.

### Step 2 — Coder responds

For `critical` and `major` findings, the coder attempts up to 3 auto-fix cycles (rebuild, retest, re-review after each).

For each meaningful finding, the coder must disposition it with one of:

- `fixed`
- `disagree-with-evidence`
- `defer`

`open` is not a valid end-state. Every finding must reach a terminal status before the run closes.

### Step 3 — Adversary re-checks unresolved items

The adversary should re-check:

- unresolved items
- disputed items
- fixes that may still hide risk

### Step 4 — Update disposition log

All meaningful findings must be reflected in `disposition-log.md`.

When a finding is deferred, record a named follow-up action whenever practical.

### Step 5 — Determine gate state

Gate state is determined by remaining unresolved findings:

- Any `critical` or `major` still unresolved → **FAIL** (blocked)
- All `critical`/`major` resolved; `minor` or `nit` remain → **WARN**
- All findings resolved → **PASS**

### Step 6 — Reconcile final artifacts

Before final completion is reported, reconcile:

- finding counts
- final gate state
- accepted-risk and deferred-item reporting
- artifact links in the execution report

## Blocking rule

Unresolved `critical` or `major` findings block completion.

At the end of the run, explicitly state:

- whether a `critical` or `major` finding remains unresolved
- whether the run is blocked
- whether human arbitration is required

## Accepted risk

`accepted-risk` means:

- the issue is real
- it is not being fixed in the current run
- a human explicitly accepts proceeding anyway

Do not use `accepted-risk` as a synonym for unresolved disagreement. If the coder disputes the finding, use `disagree-with-evidence` and record the counter-evidence.

## Human arbitration

Use human arbitration when:

- unresolved `critical` findings remain after 3 auto-fix cycles
- `major` findings remain disputed after reviewer and coder cannot converge on evidence
- the adversarial review directly contradicts the code review on the same finding
- reviewer and coder cannot converge using evidence after bounded review rounds

Recommended bound:

- 2 review rounds before escalation

Document the human decision in `disposition-log.md` and any supporting run artifact required by the workflow.

## Artifact expectations

Use the canonical templates under `.github/docs/templates/`.

Required behavior:

- keep the artifact concise
- use repo-relative paths where practical
- write `None` in required sections with no content
- do not restate `AERS.md`

## Do Nots

- Do not invent new status labels or silently alias them to the canonical
  vocabulary.
- Do not invent new severity labels; use `critical`, `major`, `minor`, `nit`.
- Do not treat green validation alone as permission to skip review or
  disposition artifacts.
- Do not use `accepted-risk` to hide unresolved disagreement without explicit
  human acceptance.
- Do not leave any finding in `open` status at run close.

## Closed Decisions

- The workflow artifact set and document structure come from the canonical
  process docs and templates.
- The status vocabulary is fixed: `open`, `fixed`, `disagree-with-evidence`,
  `defer`, `accepted-risk`, `resolved`.
- Unresolved `critical` or `major` findings block completion.
- Accepted risk requires explicit human acceptance; it is not a model-only
  decision.

## Auditor mindset

A senior developer should be able to read the review artifacts and answer:

- what findings were raised
- what evidence supported them
- how the coder responded
- whether the adversary agreed
- whether a human had to decide
- whether the run completed, blocked, or proceeded with accepted risk
