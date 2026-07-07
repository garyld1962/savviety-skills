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

> **Built-in first:** Use `/plan` for simple planning. This prompt adds a readiness gate and governed execution flow on top.

Use this prompt to begin implementation work while following the repo's Copilot-native flow.

Follow these assets:

- `.github/skills/copilot-platform-playbook/SKILL.md`
- `.github/skills/execution-environment/SKILL.md`
- `.github/skills/prd-readiness/SKILL.md`
- `.github/agents/prd-quality-gate.agent.md` when a specialist readiness pass is useful

If the user does not supply an artifact and `AERS.md` exists, treat `@AERS.md` as the starting requirements document.

## When to Use

- Starting standard feature work from an AERS, PRD, story, or spec
- Work is routine enough that governed artifacts aren't required
- You want an autonomous readiness → plan → implement → review flow

## When NOT to Use

- Work needs audit-grade traceable review artifacts — use a project-specific governed workflow
- You already have a written plan — use `prompts/dev/execute-plan.prompt.md`
- You only need planning, not implementation — use built-in `/plan`

## Arguments

- `<path>` — path to the requirements artifact (AERS, PRD, spec, story). Defaults to `AERS.md` if it exists.
- `--skip-readiness` — skip the readiness gate (use only for trivial or already-vetted changes)

## Workflow

Use the **small change fast path** when the ask is a routine, low-risk, convention-bound edit such as a single-file change, project-file metadata, template-aligned settings, or another update where repo conventions already settle the choice.

### Phase 1: AERS Readiness Gate

Run this phase unless `--skip-readiness` is passed or the small change fast path applies.

Follow `.github/skills/prd-readiness/SKILL.md` to evaluate whether the artifact is implementation-ready. The gate checks:

- All acceptance criteria are concrete and testable
- No blocking ambiguities remain (unknowns that would force a mid-implementation guess)
- Scope boundaries are clear (what is and isn't in this change)
- Any external dependencies or contracts are identified

**If readiness fails:** Do NOT proceed to planning. Report the specific gaps found, ask one clarifying question at a time, and wait for resolution. Produce only the lightest useful additions: gap report, proposed closed decisions, contract examples, verification matrix, or UI behavior matrix.

**If readiness passes** (or fast path): Proceed to Phase 2.

### Phase 2: Plan

Once the artifact is ready enough to build:

1. Detect the execution environment before emitting commands (reference `.github/skills/execution-environment/SKILL.md`).
   - State `Detected mode`, `Execution strategy`, and `Why` only when shell choice is ambiguous, the user needs commands, or the environment affects the implementation.
   - If the environment is obvious and no shell guidance is needed, detect it silently and continue.
2. Use the built-in `/plan` flow for implementation planning. Do not invent a separate planning process.
   - Skip `/plan` for the small change fast path unless the user asked for a plan or the work expands beyond a routine edit.
3. Validate the plan before proceeding:
   - Every planned step maps to a concrete acceptance criterion
   - No step relies on an assumption that wasn't in the artifact
   - The plan does not introduce scope beyond what the artifact describes
   - If the plan fails this check, revise it before moving to implementation

### Phase 3: Implement

After planning, implement autonomously:

- Inspect the repo structure and relevant files
- Make precise changes
- Run only the existing build, test, lint, or validation commands that already belong to the repo (do not invent new commands)
- Use background tasks or parallel agents when helpful
- Continue until the change is verified or a real blocker is reached

### Phase 4: Review

After implementation, choose the review depth that fits the risk:

- Use built-in `/review` for the quick/default path
- Use `prompts/review/domain-review.prompt.md` for a deeper defect-focused pass
- Use `prompts/review/professional-review.prompt.md` when the code may work but the engineering choices need a senior-bar review
- If deeper skepticism is needed after that, use `prompts/dev/adversarial-review.prompt.md`

## Output contract

Keep updates concise.

- For multi-step or ambiguous work, cover:
  - requirement readiness (gate result)
  - environment decision
  - plan status
  - implementation progress
  - validation results
  - remaining blocker or next step
- For the small change fast path, skip phase-by-phase narration and report only the decision-driving context, concrete edits, validation, and any real blocker.

## CRITICAL: Do Not Guess

- Do NOT proceed past the readiness gate if blocking ambiguity remains.
- Do NOT reopen closed decisions that are already settled in the artifact.
- Do NOT emit shell commands before detecting the environment.
- Do NOT skip readiness checks when the requirements are still ambiguous.
- Do NOT replace `/plan` or `/review` with a giant custom prompt workflow.
- Do NOT claim completion without running the repo's existing validation steps.
- Do NOT narrate obvious implementation defaults unless they conflict with repo conventions or create a user-visible tradeoff.
- Do NOT consult `CLAUDE.md` — this repo's conventions live in `copilot-instructions.md`.
