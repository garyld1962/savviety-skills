# Execution Workflow Process

This document defines the execution phases for governed autonomous development in this project. Edit the phases, gates, and thresholds to match your project's needs.

## Execution Phases

### Phase 1 — Readiness Gate

Before implementation begins, verify the requirements artifact is implementation-ready:
- No blocking ambiguity remains
- Acceptance criteria are testable
- Scope is bounded

If readiness fails, resolve gaps before proceeding. Do not start coding with open questions.

### Phase 2 — Planning

Produce an implementation plan that covers:
- Task breakdown with dependency ordering
- Affected files and packages
- Test strategy (what to test, how to verify)
- Risk areas

### Phase 3 — Implementation

Execute the plan in dependency order:
- Build and test after each logical chunk
- Stop on real blockers — do not skip ahead
- Follow the plan literally unless the user explicitly approves a deviation

### Phase 4 — Validation

Run the project's configured quality checks:
- Lint, build, typecheck
- Unit and integration tests for affected scope
- Any project-specific verification steps

### Phase 5 — Code Review

Write `review-code.md` using the project's review template. Follow the evidence standard from `evidence-and-artifacts.md`.

### Phase 6 — Elevation Pass

After green validation, check whether the code meets the senior-developer baseline at high-leverage seams. Only recommend improvements that buy concrete value.

### Phase 7 — Adversarial Review

Write `adversarial-review.md`. Use a different model or distinct reviewer role when possible.

### Phase 8 — Disposition Loop

Follow the disposition process from `review-and-disposition.md`:
- Reviewer raises → Coder responds → Adversary re-checks → Log updated
- Repeat until convergence or escalation threshold

### Phase 9 — Gate Verdict

Determine run state:
- `completed`
- `completed-with-accepted-risk`
- `blocked`
- `awaiting-human-decision`

### Phase 10 — Closeout

Write `execution-report.md`. Reconcile all artifacts. Report final state.

## Customization

Edit this file to:
- Add or remove phases for your project
- Change gate thresholds (e.g., require 3 review rounds instead of 2)
- Add project-specific validation steps
- Define which phases are skippable for different risk levels
