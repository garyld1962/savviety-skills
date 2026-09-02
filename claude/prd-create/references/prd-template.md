# PRD.md template

Written by `/prd-create` **Step 5** to `docs/prds/<slug>/PRD.md`. Sections marked
*(brownfield)* or *(rewrite only)* are conditional; drop them otherwise rather
than leaving them empty. The PRD is the human-readable half: it carries no
Public API, Data Models, Verification Matrix, Repo Starting State, Tooling
Assumptions, Execution Preflight or Readiness Assessment — those are generated
into the sibling `AERS.md` in Step 7. Content flows PRD → AERS, never back.

```markdown
# PRD: <Title>

Date: <YYYY-MM-DD>
Status: draft | reviewed | approved
Owner: <name>
Mode: greenfield | feature | refresh | rewrite
Thesis: <one sentence>
Siblings: ./AERS.md · ./ONTOLOGY.md · ./UBIQUITOUS_LANGUAGE.md

## Summary

<Three to five sentences a stakeholder can read cold.>

## Problem and Outcome

- Current pain:
- Affected users:
- Desired outcome:
- Success signal:

## Thesis and UoD Boundary

Thesis: <the sentence the release is judged against>

Representable this release:
- <fact the system can hold>

Not representable this release:
- <fact deliberately outside the universe of discourse>

Scope bounds the work; the UoD bounds representable truth. See ./ONTOLOGY.md.

## Users and Actors

| Actor | Goal | Permissions boundary |
|---|---|---|

## Scope

In scope:
- ...

Out of scope:
- ...

Later:
- ...

## Current State → Target State  *(brownfield: feature, refresh, rewrite)*

Shape: <language · project type · size class · test signal>  *(refresh)*

| Aspect | Current | Target | Change class |
|---|---|---|---|
| <surface or behaviour> | <what the code does today, with a path> | <what it must do> | addition \| revision |

## Functional Requirements

- **FR-1** — The system **shall** … using **<Entity>** … *(alethic | deontic)*
- **FR-2** — …

Every bold term resolves to a row in ./ONTOLOGY.md.

## Non-functional Requirements

- Performance:
- Security and permissions:
- Operability:

## Acceptance Criteria

- [ ] <criterion carrying a load-bearing ontology constraint, e.g. a second
      **Order** with the same order_number is rejected>
- [ ] <criterion for a mandatory role>
- [ ] <criterion for lifecycle totality>

## Closed Decisions

Product-level only; engineering decisions live in ./AERS.md.

| Decision | Choice | Rationale |
|---|---|---|

## Open Decisions

| Decision | State | Re-entry condition or why unknown |
|---|---|---|

## Risks and Assumptions

- Risk:
- Load-bearing assumption:

## Non-goals

- <thing that could easily be pulled in but must not be>

## What May Change  *(rewrite only)*

Named surfaces this rewrite is permitted to change. An ontology `revision` is
allowed only when it appears in this list and is confirmed as a closed decision;
anything not listed here halts the interview.

| Surface | May change | Confirmed by |
|---|---|---|

Preserved (must not change):
- <contract the rewrite must keep>
```
