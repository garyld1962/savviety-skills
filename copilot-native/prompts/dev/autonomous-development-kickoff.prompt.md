---
description: >-
  Start autonomous development from a PRD, story, or repo ask by following this
  repo's environment-check, PRD-readiness, planning, implementation, and review
  flow without duplicating Copilot built-ins.
argument-hint: "[@artifact path, feature ask, or area to build; defaults to @AERS.md when relevant]"
agent: "agent"
tools:
  - read
  - search
  - edit
  - execute
  - codebase
---

# Autonomous Development Kickoff

Use this prompt to begin implementation work while following the repo's Copilot-native flow.

Follow these assets:

- `.github/skills/copilot-platform-playbook/SKILL.md`
- `.github/skills/execution-environment/SKILL.md`
- `.github/skills/prd-readiness/SKILL.md`
- `.github/agents/prd-quality-gate.agent.md` when a specialist readiness pass is useful

If the user does not supply an artifact and `AERS.md` exists, treat `@AERS.md` as the starting requirements document.

## Workflow

Use the **small change fast path** when the ask is a routine, low-risk, convention-bound edit such as a single-file change, project-file metadata, template-aligned settings, or another update where repo conventions already settle the choice.

1. Read the exact artifact or files the user supplied. Prefer `@file` context and exact repo inspection over guesses.
2. Detect the execution environment before emitting commands.
   - State `Detected mode`, `Execution strategy`, and `Why` only when shell choice is ambiguous, the user needs commands, or the environment affects the implementation.
   - If the environment is obvious and no shell guidance is needed, detect it silently and continue.
3. Check whether the requirements are implementation-ready.
   - For the small change fast path, do not reopen routine implementation defaults that are already implied by repo conventions, SDK defaults, templates, or the user's direct ask.
   - If blocking ambiguity remains, do **not** start coding yet.
   - Ask one question at a time.
   - Produce only the lightest useful additions: gap report, proposed closed decisions, contract examples, verification matrix, or UI behavior matrix.
   - Use the `prd-quality-gate` agent if a focused readiness review will help.
4. Once the artifact is ready enough to build, use the built-in `/plan` flow for implementation planning instead of inventing a separate planning process.
   - Skip `/plan` for the small change fast path unless the user asked for a plan or the work expands beyond a routine edit.
5. After planning, implement autonomously:
    - inspect the repo structure and relevant files
    - make precise changes
   - run only the existing build, test, lint, or validation commands that already belong to the repo
   - use background tasks or agents when helpful
   - continue until the change is verified or a real blocker is reached
6. After implementation, use `/review` for a default review pass. If deeper skepticism is needed, use `.github/prompts/dev/adversarial-review.prompt.md` after switching models.

## Output contract

Keep updates concise.

- For multi-step or ambiguous work, cover:
  - requirement readiness
  - environment decision
  - plan status
  - implementation progress
  - validation results
  - remaining blocker or next step
- For the small change fast path, skip phase-by-phase narration and report only the decision-driving context, concrete edits, validation, and any real blocker.

## CRITICAL: Do Not Guess

- Do NOT reopen closed decisions that are already settled in the artifact.
- Do NOT emit shell commands before detecting the environment.
- Do NOT skip readiness checks when the requirements are still ambiguous.
- Do NOT replace `/plan` or `/review` with a giant custom prompt workflow.
- Do NOT claim completion without running the repo's existing validation steps.
- Do NOT narrate obvious implementation defaults unless they conflict with repo conventions or create a user-visible tradeoff.
