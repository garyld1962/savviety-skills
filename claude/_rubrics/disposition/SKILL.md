---
name: disposition
description: "Governance rules for plan review, code review, adversarial review, finding disposition, accepted-risk handling, and human arbitration in autonomous execution workflows. Not user-invokable — referenced by execute-workflow, postmortem, kickoff."
---

# Review and Disposition Governance

Use this rubric when the workflow includes review artifacts such as:

- review-plan
- review-code
- adversarial-review
- disposition-log
- human arbitration or accepted-risk decisions

## Core Principle

> Green validation is not enough. Completion requires evidence-based review and explicit disposition of meaningful findings.

## Senior Baseline Principle

Use a minimum senior-developer baseline at high-leverage seams:

- public API shape
- module boundaries
- ownership of data and responsibilities
- validation and error handling
- observability and diagnosability
- extension points

Do not interpret this as a requirement to polish every line equally.

## Source of Truth

Workflow and artifact structure are defined in the project's process docs and artifact templates. These are per-project files authored by the user (see `/configure workflow`).

Do not invent a different report structure if a canonical template already exists in the project.

## Required Review Set

The canonical review set contains:

- review-plan
- review-code
- adversarial-review
- disposition-log

Use only the artifacts relevant to the run, but do not silently skip required gates defined by the workflow.

## Adversarial Review Independence

The adversarial review should be meaningfully independent from the main implementation path.

Preferred order:

1. use a different frontier model family
2. if unavailable, use a different model variant
3. in all cases, keep the adversarial role and evaluation criteria distinct

## Evidence Standard

A meaningful finding must be evidence-based.

Include:

- severity
- evidence
- why it matters
- recommended fix

Do not drive the loop with:

- style-only commentary
- speculative requirements
- unsupported objections

## Elevation Pass Rule

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

## Proof Accounting Rule

The code review should explicitly classify major behavioral areas as:

- `proved`
- `partially proved`
- `unproved`

Do not let green tests imply stronger proof than the evidence supports.

## Status Vocabulary

Use only:

- `open`
- `fixed`
- `disagree-with-evidence`
- `defer`
- `accepted-risk`
- `resolved`

## Disposition Loop

### Step 1 — Reviewer raises findings

Reviewers write only high-signal findings in the appropriate review artifact.

### Step 2 — Coder responds

For each meaningful finding, the coder must disposition it with one of:

- `fixed`
- `disagree-with-evidence`
- `defer`

### Step 3 — Adversary re-checks unresolved items

The adversary should re-check:

- unresolved items
- disputed items
- fixes that may still hide risk

### Step 4 — Update disposition log

All meaningful findings must be reflected in the disposition log.

When a finding is deferred, record a named follow-up action whenever practical.

### Step 5 — Determine gate state

Completion depends on the remaining unresolved findings.

### Step 6 — Reconcile final artifacts

Before final completion is reported, reconcile:

- finding counts
- final gate state
- accepted-risk and deferred-item reporting
- artifact links in the execution report

## Blocking Rule

Unresolved `High` findings block completion.

At the end of the run, explicitly state:

- whether a `High` finding remains unresolved
- whether the run is blocked
- whether human arbitration is required

## Accepted Risk

`accepted-risk` means:

- the issue is real
- it is not being fixed in the current run
- a human explicitly accepts proceeding anyway

Do not use `accepted-risk` as a synonym for unresolved disagreement.

## Human Arbitration

Use human arbitration when:

- unresolved `High` findings remain after bounded review rounds
- important `Medium` findings remain disputed after bounded review rounds
- reviewer and coder cannot converge using evidence

Recommended bound:

- 2 review rounds before escalation

Document the human decision in the disposition log and any supporting run artifact required by the workflow.

## Artifact Expectations

Use the project's canonical templates (see `/configure workflow` for template locations).

Required behavior:

- keep the artifact concise
- use repo-relative paths where practical
- write `None` in required sections with no content
- do not restate the requirements document

## Auditor Mindset

A senior developer should be able to read the review artifacts and answer:

- what findings were raised
- what evidence supported them
- how the coder responded
- whether the adversary agreed
- whether a human had to decide
- whether the run completed, blocked, or proceeded with accepted risk
