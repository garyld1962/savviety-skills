---
name: aers-readiness
description: "Reusable rubric defining the AERS (Agent-Executable Requirements Spec) readiness standard — required sections, closed-decision categories, ambiguity priorities, interaction rules, and the composite readiness score that adds the ontology verdict from _internal/ontology-readiness to the structural score. Consumed by /prd-validate, /kickoff, /execute-prd, and /spec-review-adversarial. Not user-invokable."
user-invocable: false
internal: true
kind: reference
---

# AERS Readiness Rubric

Use this skill to evaluate or improve a requirements artifact before implementation planning.

**Preferred term:** **AERS** — Agent-Executable Requirements Spec.

## When to Use

- Scoring or shaping a requirements artifact against the readiness rubric
- Referenced internally by `/prd-validate`, `/kickoff`, `/execute-prd`, and `/spec-review-adversarial` for their gates
- You need the authoritative definition of "implementation-ready"

## When NOT to Use

- You want an interactive interview to fix gaps — use `/prd-validate`
- Verifying completed work against a finished implementation — use `/prd-acceptance`
- Drafting a PRD from scratch — use `/prd-create`, which owns the blank-start interview
- Scoring the artifact's *semantics* rather than its structure — use `_internal/ontology-readiness`

## Input → Output Model

### Typical input

- business problem statement
- business-oriented PRD or BRD
- story or epic
- stakeholder notes
- partial engineering spec
- rough idea

### Expected output

- an **AERS** — a requirements artifact executable by engineers and coding agents with minimal re-interpretation

## Core Principle

> If the author already knows a fact, the artifact should say it.

Reduce execution drift by surfacing settled facts early.

## Relationship to Other Skills

- Use `/prd-validate` to run this rubric interactively
- Use `/kickoff` or `/execute-prd` after the artifact is ready
- Use `superpowers:writing-plans` for implementation planning (not this skill)
- `_internal/ontology-readiness` owns the semantic half: it produces the `Ontology:` verdict line and a capped composite contribution. This rubric owns the structural score and combines the two — see **Composite score** below.
- Use `/prd-create` to draft a PRD and its `ONTOLOGY.md` from a blank start, or to extend an existing one
- BA plugin skills (`ba-problem-refiner`, `ba-spec-engineer`) can feed into this rubric

## Entry Modes

### Existing artifact

When the user provides a document (AERS, BRD, story, notes):
- Preserve what is already known
- Identify gaps
- Upgrade the artifact into an AERS

### Blank start

When the user only has an idea, `/prd-create` owns the blank-start interview and
writes the PRD folder (`docs/prds/<slug>/`, including its `ONTOLOGY.md`). This
rubric scores what that interview produces; it does not run the interview. The
sentence `/prd-create` opens with:
> "Tell me what you want to achieve in plain language. You do not need to format it yet — I will help turn it into a structured, implementation-ready artifact."

## Interaction Rules

- Ask one question at a time
- Prefer multiple-choice with a recommended default
- Explain why the question matters
- Challenge ambiguity instead of smoothing over it
- If the user says "you choose", propose a default and ask for confirmation

## What to Extract or Create

### Problem and outcome

- current pain, affected users, desired outcome, success signal

### Scope

- in scope, out of scope, MVP vs later

### Domain and workflow

The semantic content of this section — the universe of discourse, entity types
and their reference schemes, fact types, constraints, lifecycle totality,
temporality, modality, homonyms and synonyms — is defined once, as the
**Elicitation Categories** table in `_internal/ontology-readiness`. Elicit
against that table rather than a second list here, and record the result in the
artifact's `ONTOLOGY.md`.

Still elicited here, because they are computation rather than domain structure:

- formulas, calculations, tie-breakers
- normalization, rounding, precision rules

### API / integration contract

- endpoints or actions, request/response shapes
- external systems, base URL or environment contracts

### UI behavior

- main surfaces/pages, create/edit/delete flow
- inline vs full-form editing
- empty/loading/error states, sort/filter ownership

### Quality and verification

- acceptance criteria, required test layers
- test data strategy, deterministic time strategy
- error-path expectations, empty-state expectations
- aggregation/reporting verification

### Execution context

- repo starting state, target framework/runtime version
- solution/workspace format, tooling assumptions
- integration test gating, package/project boundaries

## Prioritize Ambiguity by Risk

Ask about these first:

- unclear problem statement
- unclear actor/user
- unclear scope boundary
- unclear destructive behavior
- unclear source of truth
- unclear workflow/business rules
- unclear permissions/security boundary
- unclear calculation/normalization rules
- unclear stack/platform choice that changes implementation

Then the seven **high-risk semantic ambiguity categories** named in
`_internal/ontology-readiness` § *Automated ontology check*, by their exact names
there: entity with no reference scheme; term used in a functional requirement but
absent from the ontology; non-total state machine; fact type with no constraint
and no explicit `[unconstrained]` marker; alethic/deontic conflation on a
load-bearing rule; unstated temporality on a fact that visibly changes over time;
surviving homonym.
They are scored there, not here — they feed the `Ontology:` verdict line, and
the structural list above never charges them a second time.

Then ask about defaults:

- validation approach, styling system
- server vs client responsibility
- seed/bootstrap behavior
- test scope, test data ownership
- time determinism, error UX policy

## Required Sections in an Execution-Ready AERS

- Problem Summary
- Scope
- Functional Requirements
- Closed Decisions
- Open Decisions
- Public API or Public Interface
- Domain Ontology (excluded from the per-section tally — see below)
- Data Models
- Verification Matrix / Test Strategy
- Repo Starting State
- Tooling Assumptions
- Execution Preflight
- Definition of Done
- Readiness Assessment

### Closed Decisions

Mandatory. Include settled implementation choices:
- chosen stack/framework, validation approach, persistence choice
- delete semantics, styling system, migration/bootstrap behavior
- API contract style, testing expectations, required test layers
- test data creation strategy, time/clock determinism strategy
- error handling policy, normalization/precision/tie-breaker rules

### Open Decisions

List decisions still unresolved that could materially change implementation. Do not hide these in narrative prose.

### Public API / Interface

When the solution exposes code, APIs, commands, events, or library methods, define the intended public surface: public methods, endpoint set, CLI, event contract, service interface.

### Domain Ontology

Always points at the sibling `ONTOLOGY.md` in the artifact's `docs/prds/<slug>/` folder. There is no inline alternative — the ontology check scores the sibling file, so an inlined ontology reads as a missing one. Proportionality comes from the trivial-domain rule in `_internal/ontology-readiness`, which is the only escape; a legacy bare `.md` artifact with no folder of its own has no sibling, so its ontology resolves to missing and that rule decides between `Absent (trivial domain)` and a bare `Absent`. The notation, the file format, the item-state vocabulary, and the scoring all live in `_internal/ontology-readiness`; do not restate them here.

This section is **excluded from the per-section 0/1/2 tally** in the **Automated readiness check** below. Its contribution to the composite arrives through the ontology check instead, so tallying it structurally as well would charge the same gap twice.

### Data Models

Define structures that callers, APIs, or persisted entities depend on: field names, required vs optional, type expectations, enum/state values, normalization rules.

The ontology describes the world; `Data Models` describes the representation. The ontology *feeds* `Data Models` and `Closed Decisions`. Keep the two separate, or the domain quietly becomes whatever the current schema happens to be.

### Verification Matrix

| Layer | Required | What Must Be Proven | Notes |
|---|---|---|---|
| API integration | Yes | CRUD, filtering, validation, 404 paths | Use real DB if practical |

At minimum decide: unit vs data vs API vs browser test layers, whether tests must create their own data, how time-sensitive logic is made deterministic, whether stats/reporting needs deep assertions.

### Execution Preflight

Before implementation begins, make explicit:
- target framework or runtime version
- empty repo vs scaffolded vs existing
- solution/project/workspace format
- whether scaffolding should happen first
- how integration tests are gated
- whether package/project boundaries already exist

### UI Behavior Matrix (when UI work exists)

| Surface | User Action | Expected Behavior | Validation / Error Notes |
|---|---|---|---|
| New item form | Click Save | Record created, redirect to detail | Inline field errors on invalid |

### Readiness Assessment

End with:
```
Readiness: Not ready / Partially ready / Ready
Ontology: Ready / Partial / Absent

Structural score: <n>
Ontology contribution: <0 | +2 | +4>
Composite: <n>

Blocking gaps:
- ...

Recommended follow-ups:
- ...
```

`Ontology:` is copied verbatim from `_internal/ontology-readiness`, including the
`(trivial domain)` qualifier when that rule fires. `Structural score` is the
per-section and ambiguity total from the **Automated readiness check**;
`Composite` is the sum the verdict thresholds are read against.

## Automated readiness check (for callers)

`/kickoff` and `/execute-prd` need to decide whether to suggest the
interactive `/prd-validate` interview or proceed without it. Use this
deterministic heuristic — do not invent your own.

Compute the **structural score** by inspecting the artifact for the
**Required Sections** above, excluding **Domain Ontology** — that section is
scored by the ontology check instead. For each remaining section:

- **Present and substantive** (not just a heading; has at least one
  concrete bullet, table row, or sentence specific to this work) →
  **0 points**.
- **Present but stub** (heading exists but body is "TBD" /
  "TODO" / empty / generic boilerplate) → **1 point**.
- **Missing entirely** → **2 points**.

Also score these high-risk ambiguity categories (each unresolved one
adds **2 points**):

- unclear problem statement
- unclear actor/user
- unclear scope boundary
- unclear destructive behavior
- unclear source of truth
- unclear workflow/business rules
- unclear permissions/security boundary
- unclear calculation/normalization rules
- unclear stack/platform choice that changes implementation

That total is the **structural score**. It is not the number the thresholds are
read against.

### Composite score

Run `_internal/ontology-readiness` over the same artifact (plus its sibling
`ONTOLOGY.md`, if one exists). It returns the verdict line

```
Ontology: Ready / Partial / Absent
```

and a capped contribution:

```
Composite contribution: Ready → 0, Partial → +2, Absent → +4 (cap 4)
```

The composite is

```
composite = structural score + ontology contribution
```

and it is the composite, not the structural score, that the thresholds below are
read against. The bands are unchanged by this addition. The cap keeps ontology
gaps from dominating: they get their own verdict line, they do not rewrite the
structural picture.

`Ontology: Absent (trivial domain)` — the trivial-domain rule in
`_internal/ontology-readiness` — contributes **0**. The **structural verdict** is
the structural score alone read against the same bands below; the composite
verdict is the composite read against them.

Callers halt only when the ontology line is a bare `Ontology: Absent` **and**
the structural verdict is `Partially ready` or worse. A structural verdict of
`Ready` with a bare `Absent` proceeds and logs the missing ontology as a known
risk. `Ontology: Absent (trivial domain)` never halts.

Item-state vocabulary (`settled`, `deferred` with its re-entry condition,
`unknown`) is defined once, in `_internal/ontology-readiness` § *Item states*,
and is cited here rather than redefined. It maps onto this rubric's sections:
`settled` items belong in **Closed Decisions**; `deferred` (with its condition)
and `unknown` items belong in **Open Decisions**, not in narrative prose.

### Verdict thresholds

| Composite points | Readiness | Caller behavior |
|---|---|---|
| `0–2` | **Ready** | Proceed without `/prd-validate`. Note any single gap inline. |
| `3–6` | **Partially ready** | **Suggest** `/prd-validate` to the operator, but do not auto-invoke. In autonomous mode (no human at the keyboard), proceed and log the gap list as a known risk. |
| `7+` | **Not ready** | **Do not** draft a plan. In interactive mode, suggest `/prd-validate` to close gaps. In autonomous mode, halt with a `requirements-incomplete` finding and the gap list. |

**The ontology halt is a combination, not a band.** It applies across all three
rows above and is decided on the *structural* verdict, not the composite:
Callers halt only when the ontology line is a bare `Ontology: Absent` **and**
the structural verdict is `Partially ready` or worse. A structural verdict of
`Ready` with a bare `Absent` proceeds and logs the missing ontology as a known
risk. `Ontology: Absent (trivial domain)` never halts.

Callers (`/kickoff` step 2, `/execute-prd` step 4) report the result as:

```
Readiness: Not ready / Partially ready / Ready
Ontology: Ready / Partial / Absent

Structural score: <n>
Ontology contribution: <0 | +2 | +4>
Composite: <n>

Gaps:
- ...
```

Both lines are always emitted, even when the ontology contribution is 0 — a
silent `Ontology:` line is indistinguishable from a check that was never run.

### Why "suggest, don't auto-invoke"

`/prd-validate` is an interactive interview, not a gate. Auto-invoking
it from a non-interactive context (CI, autonomous run, scheduled
agent) hangs waiting for input. Callers must respect the interaction
boundary: `/prd-validate` runs only when a human is supervising.

The score is the gate; the interview is the remedy.

## Engineering Hardening Rule

If the input is a business PRD, do not simply polish it. Transform it into an engineer-executable AERS by adding the missing required sections.

## Success Criteria

This rubric succeeds when:
- the artifact says what is already known
- unresolved ambiguity is explicit
- downstream planning no longer needs to re-derive core decisions
- test and UX expectations are clear enough to verify implementation later
- the output is clearly an AERS, not just a business PRD with nicer wording

## Contract

- **Inputs:** a requirements artifact in any flavor (PRD, BRD, story, notes, partial spec, prompt); optionally the sibling `docs/prds/<slug>/ONTOLOGY.md` when one exists. Optional repo audit from `/audit-existing` for repo-specific readiness scoring.
- **Preconditions:** the artifact is text and readable; this is a reference rubric, not an interactive interview (`/prd-validate` is the interactive remedy).
- **Outputs:** a deterministic **composite** score using the **Automated readiness check** above — structural points plus the ontology contribution, read against the unchanged bands (`Ready` 0–2, `Partially ready` 3–6, `Not ready` 7+); the `Ontology: Ready / Partial / Absent` line copied verbatim from `_internal/ontology-readiness`, with the numeric structural score and composite recorded alongside it; a gap list keyed to required sections and high-risk ambiguity categories; either an upgraded AERS (when used as a transformation pass) or recommendations.
- **Postconditions:** caller (`/prd-validate`, `/kickoff`, `/execute-prd`, `/spec-review-adversarial`) acts per the verdict thresholds; the artifact's existing closed decisions are preserved.
- **Failure modes:** artifact unreadable / not text → return `Not ready` with the file-access error in the gap list; composite `7+` in autonomous mode → halt with a `requirements-incomplete` finding; callers halt only when the ontology line is a bare `Ontology: Absent` **and** the structural verdict is `Partially ready` or worse — a structural verdict of `Ready` with a bare `Absent` proceeds and logs the missing ontology as a known risk, and `Ontology: Absent (trivial domain)` never halts; never invent answers (or an ontology) to close gaps; never auto-invoke `/prd-validate` or `/prd-create` from a non-interactive context.
