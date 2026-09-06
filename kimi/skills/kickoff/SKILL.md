---
name: kickoff
description: 'Use for operator-supervised feature work from a PRD/story/AERS: readiness
  → plan → implement → review, with the operator at the keyboard. Does not produce
  audit-grade governed artifacts; for an unattended run use /execute-prd.'
whenToUse: 'Use for operator-supervised feature work from a PRD/story/AERS: readiness
  → plan → implement → review, with the operator at the keyboard. Does not produce
  audit-grade governed artifacts; for an unattended run use /execute-prd.'
type: flow
disableModelInvocation: false
---


# /skill:kickoff — Interactive Development Start

**Purpose:** Begin implementation work from a requirements artifact with the operator at the keyboard, following a built-in-first flow: readiness check → plan → implement → review. Does NOT produce audit-grade governed artifacts; for an unattended run, use `/skill:execute-prd`.

Before the first user update, read [simplify](../simplify/SKILL.md) and apply its
output guidance to all assistant-written progress, readiness, task and review
summaries, blockers, decisions, and final results. Preserve technical evidence.

## When to Use

- Starting standard feature work from an AERS, PRD, story, or spec
- Work is routine enough that governed artifacts aren't required
- You want an operator-supervised readiness → plan → implement → review flow

## When NOT to Use

- Work needs audit-grade traceable review artifacts — use a project-specific governed workflow
- You already have a written plan — use `/skill:execute-plan`
- You only need planning, not implementation — use `superpowers:writing-plans`

## Arguments

- `<path>` — path to the requirements artifact (AERS, PRD, spec, story). If not provided, resolve it by the order below.
- `--skip-readiness` — skip the readiness scoring and the ontology halt.
  It never skips the ontology revision halt, which is a reopened-decision
  guard rather than a scoring step.

Resolution order — first match wins:

1. The explicit `<path>` argument, if one was supplied.
2. The most recently modified `docs/prds/*/AERS.md`.
3. `./AERS.md` (legacy root location).
4. The most recently modified `docs/prds/*/PRD.md`.
5. `./PRD.md`.
6. `./prompt.md`.

If two or more candidates tie within the same tier, do not guess: ask the
operator which is canonical (interactive) or emit a `plan-ambiguity` finding
and stop (autonomous).

Sibling artifacts — `ONTOLOGY.md`, `UBIQUITOUS_LANGUAGE.md`, and `PRD.md` —
resolve relative to the directory of the resolved requirements file, not the
repo root.

## Workflow

### Small Change Fast Path

When the ask is a routine, low-risk, convention-bound edit (single-file change, template-aligned config, metadata update):
- Do not reopen routine implementation defaults settled by repo conventions
- Skip phase-by-phase narration
- Report only the decision-driving context, concrete edits, validation, and any real blocker

### Standard Path

0. **Load project memory.** Check `~/.claude/agent-memory/<repo-slug>/` for a `kickoff-context.md` file, where `<repo-slug>` is the current repo's directory name. If it exists, read it — it contains architectural decisions, patterns, and constraints from prior sessions. Surface any relevant entries as "Loaded from project memory: ..." before proceeding. If the directory doesn't exist, skip silently.

1. **Read the artifact.** Read the exact artifact or files the user supplied. Prefer reading actual files over guessing content. If no path is given, resolve one:

   Resolution order — first match wins:

   1. The explicit `<path>` argument, if one was supplied.
   2. The most recently modified `docs/prds/*/AERS.md`.
   3. `./AERS.md` (legacy root location).
   4. The most recently modified `docs/prds/*/PRD.md`.
   5. `./PRD.md`.
   6. `./prompt.md`.

   If two or more candidates tie within the same tier, do not guess: ask the
   operator which is canonical (interactive) or emit a `plan-ambiguity` finding
   and stop (autonomous).

   Sibling artifacts — `ONTOLOGY.md`, `UBIQUITOUS_LANGUAGE.md`, and `PRD.md` —
   resolve relative to the directory of the resolved requirements file, not the
   repo root.

2. **Check readiness.** Unless `--skip-readiness`, score the artifact
   with the **Automated readiness check** in
   `_internal/aers-readiness/SKILL.md`. That check is a **composite**:
   structural points plus the ontology contribution produced by
   `_internal/ontology-readiness/SKILL.md` over the sibling
   `ONTOLOGY.md`. Report both the structural verdict and the
   `Ontology:` line — the point values live in those rubrics and are
   not restated here:

   ```
   Readiness: Not ready / Partially ready / Ready
   Ontology: Ready / Partial / Absent

   Structural score: <n>
   Ontology contribution: <0 | +2 | +4>
   Composite: <n>

   Gaps:
   - ...
   ```

   Both lines are always emitted, even when the ontology contribution
   is 0. The structural verdict is the structural score read against the
   same bands (see `_internal/aers-readiness`).

   Behaviour by composite verdict:
   - **Ready** → proceed to step 3.
   - **Partially ready** → ask gap questions inline (one at
     a time); record as proposed closed decisions; offer `/skill:prd-validate`
     for a structured interview. Do not auto-invoke it.
   - **Not ready** → halt. Surface the rubric points and
     suggest `/skill:prd-validate` for the operator to close gaps; do NOT
     start coding.

   **Ontology halt.** Halt only when the ontology line is a bare
   `Ontology: Absent` **and** the structural verdict is
   `Partially ready` or worse. A structural verdict of `Ready` with a
   bare `Absent` proceeds and logs the missing ontology as a known
   risk. `Ontology: Absent (trivial domain)` never halts.

   On a halt, suggest `/skill:prd-create` to the operator and stop. Do not
   auto-invoke `/skill:prd-create` — it is an interview, the same interaction
   boundary as `/skill:prd-validate`. When the run proceeds on a bare
   `Absent`, tell the operator the ontology is missing and carry it as
   a known risk.

   Produce only the lightest useful additions: gap report, proposed
   closed decisions, contract examples. For the small change fast
   path, do not reopen routine defaults already implied by repo
   conventions.

   **Ontology revision halt.** The reopened-decision halt extends to
   the ontology. It is a reopened-decision guard, not a scoring step, so
   it runs regardless of `--skip-readiness`. An `addition` entry in the
   `ONTOLOGY.md` Extension Log passes.

   A **revision** — one of exactly five kinds per
   `_internal/ontology-readiness` § *Completeness and Extension* Rule 4:
   changed reference scheme, homonym split, tightened constraint,
   reclassified modality, retrofitted temporality — is mode-dependent, and
   the mode is read from the `mode:` header of `ONTOLOGY.md`: in `feature`
   mode any `revision` entry in the Extension Log is a halt condition and
   halts with an `ontology-revision` finding; `refresh` mode follows the
   `feature` rule, so any `revision` entry halts the same way; in
   `greenfield` mode a `revision` entry is itself a defect — nothing
   existed to revise — and halts the same way; in `rewrite` mode a
   `revision` entry must be matched by a confirmed closed decision in the
   PRD, and is a halt — the same `ontology-revision` finding — only if it
   is not.

3. **Plan.** Once the artifact is ready enough to build, use `superpowers:writing-plans` for implementation planning. Skip for the small change fast path unless the user asks for a plan or the work expands.

4. **Implement.** After planning:
   - Inspect the repo structure and relevant files
   - Make precise changes
   - Run the repo's existing build, test, lint, or validation commands
   - Use background tasks or parallel agents when helpful
   - Continue until the change is verified or a real blocker is reached

5. **Review.** After implementation, use `superpowers:requesting-code-review` or `/skill:domain-review` for a review pass.

6. **Save project memory.** After a successful review, append to `~/.claude/agent-memory/<repo-slug>/kickoff-context.md` (create if absent):
   - Architectural decisions made or confirmed during this session
   - Patterns adopted or rejected (with brief rationale)
   - Constraints discovered (e.g. "do not use X because Y")
   - Anything a future session should know before starting

   Use this format:
   ```markdown
   ## Session: <YYYY-MM-DD> — <artifact slug>
   - Decision: <what was decided and why>
   - Pattern: <what pattern was adopted or rejected>
   - Constraint: <what to avoid and why>
   ```
   Only write entries that aren't already captured in CLAUDE.md or the artifact itself.

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

- Do NOT reopen closed decisions already settled in the artifact, including `settled` rows in its `ONTOLOGY.md`.
- Do NOT skip readiness checks when requirements are still ambiguous.
- Do NOT replace built-in planning/review with a custom prompt workflow.
- Do NOT claim completion without running the repo's existing validation steps.
- Do NOT narrate obvious implementation defaults unless they create a user-visible tradeoff.

## Contract

- **Inputs:** path to a requirements artifact (or the resolution order under `## Arguments` when no path is given); optional `--skip-readiness`. Calls `_internal/aers-readiness` (composite readiness scoring), `_internal/ontology-readiness` (the `Ontology:` verdict line, reached through aers-readiness), `/skill:prd-validate` and `/skill:prd-create` (only when the operator opts in interactively), `superpowers:writing-plans` (planning), `superpowers:requesting-code-review` or `/skill:domain-review` (review). Consults `_internal/disposition` and `_internal/repo-delivery`.
- **Preconditions:** in a git repo; artifact exists and is readable; operator is at the keyboard (kickoff is interactive by design — for autonomous flow, use `/skill:execute-prd`).
- **Outputs:** code committed for the requested change; review pass recorded; concise progress updates per the output contract above (decision context, edits, validation, blockers).
- **Postconditions:** repo's existing validation steps (lint/build/test) have actually run; closed decisions added to the artifact when the operator confirms; no audit-grade governed artefacts (those belong to `/skill:execute-prd`).
- **Failure modes:** readiness `Not ready` → halt before coding; blocking ambiguity remaining → halt and ask; any closed decision in the artifact reopened → halt and surface the conflict; a bare `Ontology: Absent` with a structural verdict of `Partially ready` or worse → halt and suggest `/skill:prd-create` to the operator, never auto-invoke `/skill:prd-create` (a structural `Ready` with a bare `Absent` proceeds and logs a known risk, and `Absent (trivial domain)` never halts); an ontology revision — changed reference scheme, homonym split, tightened constraint, reclassified modality, retrofitted temporality — in `feature` mode → halt with an `ontology-revision` finding, and in `rewrite` mode → the same halt unless the `revision` entry is matched by a confirmed closed decision in the PRD (mode read from the `mode:` header of `ONTOLOGY.md`), while `addition` entries pass; this revision halt runs even under `--skip-readiness`.
