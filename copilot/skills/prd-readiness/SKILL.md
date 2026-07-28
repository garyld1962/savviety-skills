---
name: prd-readiness
description: Interactive checklist and workflow for turning a story, BRD, AERS draft, or rough idea into an implementation-ready artifact for GitHub Copilot workflows.
---

# AERS Readiness

Use this skill to refine a requirements artifact before implementation planning.

**Preferred term:** **AERS** — Agent-Executable Requirements Spec.

This skill name remains `prd-readiness` for compatibility during migration, but the target artifact should now be described as an **AERS**.

## Input → output model

### Typical input

- business problem statement
- business-oriented PRD
- BRD
- story or epic
- stakeholder notes
- partial engineering spec

### Expected output

- an **AERS** — Agent-Executable Requirements Spec

The point of this skill is to transform a business-facing or incomplete artifact into one that is executable by engineers and coding agents.

## Core principle

> If the author already knows a fact, the artifact should say it.

The goal is to reduce execution drift and wasted reasoning by surfacing settled facts early.

## When NOT to Use

- You want an interactive interview to fix gaps — use the `prd-validator` prompt directly
- Verifying a finished implementation — use a review prompt instead
- Drafting a PRD from scratch — use `ba-problem-refiner` first

## Relationship to Copilot built-ins

- Use this skill **before** `/plan`
- Do not use this skill as a replacement for implementation planning
- Use `/review` or custom review prompts later to challenge the built implementation

## Prompt entry points in this workspace

This skill is the shared durable logic behind:

- `#prompt:prd-validator`
- `#prompt:ba-problem-refiner`
- `#prompt:ba-spec-engineer`

Use the lightest workflow that fits:

- `prd-validator` when an existing artifact needs to become an AERS
- `ba-problem-refiner` when the problem statement itself is still vague
- `ba-spec-engineer` when the user needs a fuller executable spec for handoff

## Entry modes

### Existing artifact

Use when the user provides:

- AERS
- BRD
- story
- epic
- notes doc
- draft text

Goal: preserve what is already known, identify gaps, and upgrade the artifact into an AERS.

### Blank start

Use when the user only has an idea or business problem statement.

Opening prompt:

```text
Tell me what you want to achieve in plain language. You do not need to format it yet — I will help turn it into a structured, implementation-ready artifact.
```

## Interaction rules

- Ask one question at a time
- Prefer multiple-choice with a recommended default
- Explain why the question matters
- Challenge ambiguity instead of smoothing over it
- If the user says "you choose", propose a default and ask for confirmation

## Examples

- **Upgrade a business PRD:** Preserve the known business context, extract the
  missing behavioral rules, add `Closed Decisions`, `Open Decisions`, example
  contracts, and a verification matrix, then hand off to `/plan`.
- **Blank-start refinement:** Start from a plain-language ask, ask one targeted
  question at a time, and turn the answers into an AERS instead of jumping into
  implementation steps.

## What to extract or create

The output should be engineering-oriented, not merely descriptive.

### Problem and outcome

- current pain
- affected users
- desired outcome
- success signal

### Scope

- in scope
- out of scope
- MVP vs later

### Domain and workflow

- core entities
- required vs optional fields
- enums/statuses/state transitions
- formulas, calculations, and tie-breakers
- normalization, rounding, and precision rules

### API / integration contract

- endpoints or actions
- request/response shapes
- external systems
- base URL or environment contracts

### UI behavior

- main surfaces/pages
- create/edit/delete flow
- inline vs full-form editing
- empty/loading/error states
- sort/filter ownership

### Quality and verification

- acceptance criteria
- required test layers
- test data strategy
- deterministic time strategy when relevant
- error-path expectations
- empty-state expectations
- aggregation/reporting verification

### Execution context

- repo starting state
- target framework/runtime version
- solution/workspace format
- tooling assumptions
- integration test gating
- package/project boundaries

## Prioritize ambiguity by risk

Ask about these first when unresolved:

- unclear problem statement
- unclear actor/user
- unclear scope boundary
- unclear destructive behavior
- unclear source of truth
- unclear workflow/business rules
- unclear permissions/security boundary
- unclear calculation or normalization rules
- unclear stack/platform choice that changes implementation

Then ask about defaults:

- validation approach
- styling system
- server vs client responsibility
- seed/bootstrap behavior
- test scope
- test data ownership
- time determinism
- error UX policy

## Problem refinement mode

When the prompt is `ba-problem-refiner`, bias toward:

- turning solution-shaped requests back into problem statements
- surfacing stakeholder, scope, impact, root-cause, success, and assumption gaps
- asking a short set of targeted questions before rewriting anything
- producing a concise problem statement plus a gap map

Preferred output shape:

- Problem Summary
- Current State
- Impact
- Root Cause
- Desired Future State
- Affected Stakeholders
- Scope Boundaries
- Success Criteria
- Constraints
- Assumptions
- Gap Map

## Specification engineering mode

When the prompt is `ba-spec-engineer`, bias toward:

- building a fuller execution-ready AERS or requirements specification
- interviewing in small batches instead of asking for everything at once
- making acceptance criteria independently testable
- calling out assumptions, risks, and unresolved decisions explicitly

Preferred output sections:

- Executive Summary
- Business Objectives
- Stakeholder Requirements
- Acceptance Criteria
- Constraint Architecture
- Requirements Decomposition
- Non-Functional Requirements
- Business Rules
- Evaluation Criteria
- Assumptions and Risks
- Glossary
- Definition of Done

## Required sections in the upgraded artifact

An execution-ready AERS should normally include:

- Problem Summary
- Scope
- Functional Requirements
- Closed Decisions
- Open Decisions
- Public API or public interface
- Data Models
- Verification Matrix / Test Strategy
- Repo Starting State
- Tooling Assumptions
- Execution Preflight
- Definition of Done
- Readiness assessment

If the input artifact is a business PRD, the skill should explicitly convert it into this structure rather than leaving it in business-document form.

### `Closed Decisions`

Use the exact heading if that is the project convention.

This section is mandatory in an AERS.

Include settled implementation choices such as:

- chosen stack/framework
- validation approach
- persistence choice
- delete semantics
- styling system
- migration/bootstrap behavior
- API contract style
- testing expectations
- required test layers
- test data creation strategy
- time/clock determinism strategy
- error handling policy
- normalization / precision / tie-breaker rules

### `Open Decisions`

List decisions that are still unresolved and could materially change implementation.

Do not hide these in narrative prose.

## Do Nots

- Do not reopen facts the author already settled just to create more option
  space.
- Do not drift into implementation planning, task waves, or code-level design.
- Do not hide unresolved ambiguity in narrative prose; surface it as `Open
  Decisions`, explicit gaps, or blocking readiness issues.

## Closed Decisions

- The target artifact is an **AERS**, even when the input is a PRD, BRD, story,
  or rough notes.
- This skill runs before `/plan`; it refines requirements rather than planning
  execution.
- Settled facts belong in the artifact as `Closed Decisions` so downstream work
  does not need to re-derive them.
- Ask only about decisions that are still materially open.

### Public API / Interface

When the solution exposes code, APIs, commands, events, or library methods, define the intended public surface explicitly.

Examples:

- public methods
- endpoint set
- command-line interface
- event contract
- service interface

### Data Models

Define the structures that callers, APIs, or persisted entities depend on.

Include:

- field names
- required vs optional
- type expectations
- enum/state values
- normalization rules

### Verification Matrix

Add when implementation will follow. Make the expected test shape explicit.

Suggested table:

| Layer | Required | What Must Be Proven | Notes |
|-------|----------|---------------------|-------|
| API integration | Yes | CRUD, filtering, validation, 404 paths | Use real DB if practical |

At minimum decide:

- unit vs data/repository vs API vs browser test layers
- whether tests must create their own data
- how time-sensitive logic is made deterministic
- whether stats/reporting needs deep assertions

Include rows when relevant for:

- valid filtering, not just sorting
- missing-resource `404` on mutating endpoints
- optional field omission / null / blank handling
- string boundary values
- empty database behavior
- route-not-found and global error handlers
- aggregation rules such as exclusions, rounding, and top-N ordering

### Execution Preflight

Before implementation begins, the AERS should make these explicit:

- target framework or runtime version
- empty repo vs scaffolded repo vs existing repo
- solution/project/workspace format
- whether scaffolding should happen first
- how live integration tests are gated
- whether package/project boundaries already exist

This is specifically meant to prevent avoidable execution friction such as:

- framework mismatches
- wrong solution format
- bad assumptions about repo starting state
- noisy or unsafe integration test behavior

### UI Behavior Matrix

When UI work exists, add a compact table:

| Surface | User Action | Expected Behavior | Validation / Error Notes |
|---------|-------------|-------------------|--------------------------|
| New item form | Click Save | Record created, redirect to detail | Inline field errors on invalid input |

### Readiness assessment

End with:

```text
Readiness: Not ready / Partially ready / Ready

Blocking gaps:
- ...

Recommended follow-ups:
- ...
```

## Engineering hardening rule

If the input is a business PRD, do not simply polish it. Transform it into an engineer-executable AERS by adding:

- Closed Decisions
- Open Decisions
- Public API
- Data Models
- Test Strategy
- Repo Starting State
- Tooling Assumptions
- Execution Preflight
- Definition of Done

## Stack-specific testing prompts

### .NET + EF Core

Recommend clarifying:

- shared/domain unit tests
- data or `AppDbContext` / repository tests
- API integration tests using `WebApplicationFactory`
- browser automation only when explicitly required

Prefer:

- data-layer tests when persistence includes business behavior
- test-owned data instead of hardcoded seed IDs
- deterministic clocks when time affects scoring or reports

### TypeScript + HTTP API

Recommend clarifying:

- shared/domain unit tests
- repository/data integration tests
- API tests through the app server
- browser tests only when explicitly required

Prefer:

- lifecycle hooks over repetitive per-test setup/cleanup
- test-owned data instead of brittle seed IDs
- explicit `now` or clock injection when time affects behavior

## Success criteria

This skill succeeds when:

- the artifact says what is already known
- unresolved ambiguity is explicit
- downstream planning no longer needs to re-derive core decisions
- test and UX expectations are clear enough to verify implementation later
- the output is clearly an AERS, not just a business PRD with nicer wording
