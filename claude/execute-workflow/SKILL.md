---
name: execute-workflow
description: "Governed autonomous execution with required review artifacts, disposition loop, and gate verdicts. Use when the work needs traceable review evidence, not just green tests. Heavier than /execute-plan."
---

# /execute-workflow — Governed Execution

**Purpose:** Run a governed, artifact-producing execution workflow from a requirements document. Produces review-plan, review-code, adversarial-review, disposition-log, and execution-report artifacts in the project's run folder. Use this when the work is risk-bearing or needs audit-grade traceability.

**For lightweight execution without governance artifacts, use `/execute-plan` instead.**

## When to Use

- Work is risk-bearing (auth, payments, data migrations, compliance-relevant)
- Audit-grade traceability is required — review-plan, disposition-log, etc.
- Stakeholders need evidence of review, not just green tests

## When NOT to Use

- Standard feature work without governance needs — use `/kickoff` or `/execute-plan`
- No requirements artifact exists yet — produce one first
- Quick bug fix or routine change — overhead is not justified

## Pre-flight Required Config

Before proceeding, verify:

1. Check `<project>/.claude/workflow.config.md` exists.
   If not, halt:
   > This skill requires `<project>/.claude/workflow.config.md`.
   >
   > Set it up interactively:
   > ```
   > /configure workflow
   > ```
   >
   > Or copy the template and edit manually:
   > ```
   > cp claude/execute-workflow/config.template.md <project>/.claude/workflow.config.md
   > ```

2. Read the config. Verify `process_docs_root`, `templates_root`, and `runs_root` are present and non-placeholder.
   If any field contains `<FILL IN>`, halt and list the missing fields.

3. Verify at least one process doc exists at `process_docs_root`. If the directory is empty, halt:
   > No process docs found at `<path>`.
   >
   > Copy the reference templates:
   > ```
   > cp -r claude/execute-workflow/process-docs.template/ <project>/docs/process/
   > ```
   > Then edit them for your project.

4. If healthy, proceed silently.

## Arguments

- `<path>` — path to the requirements artifact (AERS, PRD, spec). Defaults to `AERS.md` if it exists.
- `--skip-readiness` — skip the readiness gate (when requirements are already validated)
- `--small-change` — use the small change fast path (skip governed artifacts for routine edits)

## Rubrics

This skill references:
- `_rubrics/disposition` — governance rules, status vocabulary, disposition loop
- `_rubrics/repo-delivery` — delivery contracts for execution, checkpoint, ship

## Workflow

### Small Change Fast Path

Use the small change fast path when the ask is a routine, low-risk, convention-bound edit (single-file change, template-aligned config, metadata update). In this case:
- Skip governed artifacts, formal review loops, and phase-by-phase status updates
- Report only the decision-driving context, concrete edits, validation, and any real blocker
- Do NOT force the full governed workflow for changes that don't merit it

### Full Governed Path

1. **Read the requirements artifact.** If no path is given, check for `AERS.md` at the project root.

2. **Read the workflow config.** Load paths from `<project>/.claude/workflow.config.md`.

3. **Create the run folder.** Under the `runs_root` from config, create `<yyyy-mm-dd-HHMMSS>/`.

4. **Readiness gate.** Unless `--skip-readiness`, check whether the requirements are implementation-ready:
   - If blocking ambiguity remains, do NOT start coding.
   - Ask one question at a time.
   - Produce only the lightest useful additions: gap report, proposed closed decisions, contract examples.
   - Use `prd-validate` if a focused readiness review helps.

5. **Planning.** Use `superpowers:writing-plans` or `/plan` for implementation planning.

6. **Implementation.** Execute the plan:
   - Inspect the repo structure and relevant files
   - Make precise changes
   - Run the repo's existing build, test, lint, or validation commands
   - Continue until the change is verified or a real blocker is reached

7. **Code review.** Write `review-code.md` in the run folder using the project's template. Follow the disposition rubric for evidence standard and proof accounting.

8. **Elevation pass.** After green validation, run a short elevation pass per the disposition rubric. Only recommend elevation when it buys something concrete.

9. **Adversarial review.** Write `adversarial-review.md` in the run folder. If possible, use a different model or a distinct reviewer role with separate evaluation criteria.

10. **Disposition loop.** Follow the disposition rubric:
    - Reviewer raises findings → Coder responds → Adversary re-checks → Update disposition log
    - Use only the status vocabulary: `open`, `fixed`, `disagree-with-evidence`, `defer`, `accepted-risk`, `resolved`

11. **Gate verdict.** Determine the run state:
    - `completed` — all findings resolved
    - `completed-with-accepted-risk` — findings accepted by human
    - `blocked` — unresolved `High` findings remain
    - `awaiting-human-decision` — escalation needed

12. **Reconcile.** Write `execution-report.md` in the run folder. Reconcile finding counts, final gate state, accepted-risk items, and artifact links.

## Required Artifact Set

Produce in the run folder, when applicable:

| Artifact | Template source | Written when |
|---|---|---|
| `execution-report.md` | `templates_root/execution-report.template.md` | Always |
| `review-plan.md` | `templates_root/review-plan.template.md` | When a plan was produced |
| `review-code.md` | `templates_root/review-code.template.md` | Always |
| `adversarial-review.md` | `templates_root/adversarial-review.template.md` | Always |
| `disposition-log.md` | `templates_root/disposition-log.template.md` | Always |

## CRITICAL: Do Not Guess

- Do NOT restate the requirements artifact as if it were a process document.
- Do NOT invent a different artifact schema when a canonical template exists.
- Do NOT silently proceed past unresolved `High` findings.
- Do NOT end the run without a clear gate verdict.
- Do NOT route small changes through the full governed workflow unless they create a meaningful decision.
- Do NOT skip the pre-flight config check.
