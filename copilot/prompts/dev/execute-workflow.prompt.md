---
description: >-
  Start the governed execution workflow from a requirements artifact such as
  `AERS.md`, delegate to the orchestrator path, and require planning, review,
  adversarial review, and disposition artifacts before completion.
argument-hint: "[@requirements artifact, defaults to @AERS.md when relevant]"
agent: "agent"
tools:
  - read
  - search
  - edit
  - execute
  - codebase
---

# Execute Workflow

Use this prompt as the human entry point for governed autonomous execution.

Follow these assets:

- `.github/skills/copilot-platform-playbook/SKILL.md`
- `.github/skills/execution-environment/SKILL.md`
- `.github/skills/prd-readiness/SKILL.md`
- `.github/skills/review-disposition-governance/SKILL.md`
- `.github/docs/process/execute-workflow.md`
- `.github/docs/process/review-and-disposition.md`
- `.github/docs/process/evidence-and-artifacts.md`
- `.github/docs/process/document-schema.md`

If the user does not supply an artifact and `AERS.md` exists, treat `@AERS.md` as the source requirements artifact.

## Missing governed workflow assets

If any required `.github/docs/process/*.md` or `.github/docs/templates/*.template.md`
file is missing in the consuming repo:

- stop and tell the user the governed workflow support files are not installed
- name the missing path or paths explicitly
- do not invent replacement process docs, templates, or artifact schemas
- wait for the user to install the shared workflow assets or choose a lighter flow

## Workflow contract

Use this prompt for governed, multi-step, or risk-bearing execution. If the ask is a routine, low-risk, convention-bound edit, use the small change fast path instead of forcing the full governed workflow.

1. Detect the execution environment first.
   - State `Detected mode`, `Execution strategy`, and `Why` only when shell choice is ambiguous, the user needs commands, or the environment changes the execution path.
   - If the environment is obvious and no shell guidance is needed, detect it silently and continue.
2. Create or choose a run folder under `docs/runs/<yyyy-mm-dd-HHMMSS>/`.
3. Run the canonical execution phases from `.github/docs/process/execute-workflow.md`.
4. Do not skip required gates:
   - readiness gate
   - planning
   - validation
   - code review
   - elevation pass
   - adversarial review
   - disposition loop
   - closeout reconciliation
5. Use the canonical templates under `.github/docs/templates/` for all workflow artifacts.
6. Do not claim completion if unresolved `High` findings remain.
7. Tell the user explicitly at the end whether the run is:
   - `completed`
   - `completed-with-accepted-risk`
   - `blocked`
   - `awaiting-human-decision`

## Required artifact set

Produce, when applicable:

- `execution-report.md`
- `review-plan.md`
- `review-code.md`
- `adversarial-review.md`
- `disposition-log.md`

## Built-in-aware rule

- Use the small change fast path for routine edits that do not merit governed artifacts, formal review loops, or phase-by-phase status updates.
- Use `/plan` for planning.
- Use built-in review where it helps, but do not skip the required governed artifacts.
- When the default review path is not enough, use the structured `domain-review`
  lane for direct defects and `professional-review` for senior-bar engineering
  judgment, then reconcile the important conclusions into the governed review
  and disposition artifacts.
- Require a senior baseline at high-leverage seams, then run an explicit elevation pass after green validation for any worthwhile non-functional improvements.
- Prefer a different frontier model family for adversarial review when available; otherwise use a distinct reviewer role and preferably a different model variant.
- Keep this prompt thin; let process docs, templates, skills, and specialist assets define the durable rules.

## CRITICAL: Do Not Guess

- Do NOT restate `AERS.md` as if it were a process document.
- Do NOT invent a different artifact schema when a canonical template exists.
- Do NOT silently proceed past unresolved `High` findings.
- Do NOT end the run without a clear gate summary.
- Do NOT route routine implementation defaults or template-aligned project-file choices through the governed workflow unless they create a meaningful product, architectural, or cross-repo decision.
