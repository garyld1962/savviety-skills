---
name: kickoff
description: "Use for standard feature work to autonomously ship a PRD/story/AERS: readiness → plan → implement → review. Does not produce audit-grade governed artifacts."
model: opus
---

# /kickoff — Autonomous Development Start

**Purpose:** Begin implementation work from a requirements artifact, following a built-in-first flow: readiness check → plan → implement → review. Does NOT produce audit-grade governed artifacts.

## When to Use

- Starting standard feature work from an AERS, PRD, story, or spec
- Work is routine enough that governed artifacts aren't required
- You want an autonomous readiness → plan → implement → review flow

## When NOT to Use

- Work needs audit-grade traceable review artifacts — use a project-specific governed workflow
- You already have a written plan — use `/execute-plan`
- You only need planning, not implementation — use `/plan`

## Arguments

- `<path>` — path to the requirements artifact (AERS, PRD, spec, story). Defaults to `AERS.md` if it exists.
- `--skip-readiness` — skip the readiness gate

## Workflow

### Small Change Fast Path

When the ask is a routine, low-risk, convention-bound edit (single-file change, template-aligned config, metadata update):
- Do not reopen routine implementation defaults settled by repo conventions
- Skip phase-by-phase narration
- Report only the decision-driving context, concrete edits, validation, and any real blocker

### Standard Path

1. **Read the artifact.** Read the exact artifact or files the user supplied. If no path is given and `AERS.md` exists, use it. Prefer reading actual files over guessing content.

2. **Check readiness.** Unless `--skip-readiness`:
   - If blocking ambiguity remains, do NOT start coding
   - Ask one question at a time
   - Produce only the lightest useful additions: gap report, proposed closed decisions, contract examples
   - For the small change fast path, do not reopen routine defaults already implied by repo conventions
   - Use `/prd-validate` if a focused readiness review would help

3. **Plan.** Once the artifact is ready enough to build, use `superpowers:writing-plans` or `/plan` for implementation planning. Skip for the small change fast path unless the user asks for a plan or the work expands.

4. **Implement.** After planning:
   - Inspect the repo structure and relevant files
   - Make precise changes
   - Run the repo's existing build, test, lint, or validation commands
   - Use background tasks or parallel agents when helpful
   - Continue until the change is verified or a real blocker is reached

5. **Review.** After implementation, use `superpowers:requesting-code-review` or `/code-review` for a review pass.

## Output Contract

Keep updates concise:
- For multi-step work: requirement readiness, plan status, implementation progress, validation results, remaining blockers
- For small changes: decision context, concrete edits, validation, any blocker
- Do not narrate obvious implementation defaults unless they conflict with repo conventions

## Rubrics

This skill references:
- `_internal/disposition` — for governance principles (elevation pass, evidence standard) when applicable
- `_internal/repo-delivery` — for delivery contracts

## CRITICAL: Do Not Guess

- Do NOT reopen closed decisions already settled in the artifact.
- Do NOT skip readiness checks when requirements are still ambiguous.
- Do NOT replace built-in planning/review with a custom prompt workflow.
- Do NOT claim completion without running the repo's existing validation steps.
- Do NOT narrate obvious implementation defaults unless they create a user-visible tradeoff.
