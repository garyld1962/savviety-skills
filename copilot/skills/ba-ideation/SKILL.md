---
name: ba-ideation
description: Facilitate business analysis ideation from a rough idea, a single document, or a folder of documents by extracting context, surfacing gaps, comparing options, and producing workshop-ready outputs for both business and technical audiences.
---

# BA Ideation

Use this skill to help business analysts shape an idea before detailed requirements or implementation planning.

## Relationship to Copilot built-ins

- Use this skill before `/plan`
- Use this skill when the user wants to explore, frame, compare, or structure an idea
- Use `/plan` after the direction is chosen and the work is ready for implementation planning
- Use `@file` context for a specific document and exact repo inspection for a folder of docs

## Relationship to `/ideate` modes

Treat this skill as the specialist branch for `/ideate ba`.

Expected flow:

1. shared ideation establishes the problem, users, desired outcome, and major uncertainties
2. BA ideation deepens the business process, scope, assumptions, dependencies, and decision framing
3. the handoff recommends the next artifact or workflow

If `/ideate` is called without a mode and the ask is primarily business-facing, this skill is still a good default.

Quick invocation examples:

```text
/ideate ba @docs/discovery/
/ideate ba @notes/workshop-summary.md
/ideate ba "Help me shape the business process and stakeholder questions for a new approval workflow"
```

## Entry modes

### Single document

Use when the user provides one artifact such as:

- BRD
- PRD
- story
- workshop notes
- stakeholder memo
- draft proposal

Goal: extract what the document already says, identify what it implies, and turn it into a clearer ideation output without pretending the idea is implementation-ready.

### Folder of documents

Use when the user provides a folder path with multiple related artifacts.

Goal:

- identify the most relevant files
- synthesize repeated themes
- surface contradictions and missing decisions
- produce one coherent ideation summary

When working from a folder, prefer the lightest useful read set and name which files drove the conclusions.

### Blank start

Use when the user has only a rough idea.

Opening prompt:

```text
Tell me the idea in plain language. You can give me the business goal, pain point, or opportunity in rough form and I will help shape it into something we can explore with stakeholders.
```

## Audience

Default to mixed business and technical stakeholders.

Translate between:

- business outcomes and user pain
- process changes and system impacts
- stakeholder language and delivery language

## Interaction rules

- Ask one question at a time
- Prefer multiple-choice with a recommended default when practical
- Start with high-leverage ambiguity, not formatting
- Do not force implementation details too early
- Distinguish facts, assumptions, risks, and open questions
- If the user says "you choose," propose a default and explain the tradeoff briefly

## What to produce

Produce only the lightest useful set for the situation.

### Idea framing

- problem statement
- affected users or stakeholder groups
- desired outcome
- business value
- success signals or KPIs

### Current and future state

- current workflow or pain
- friction points
- future-state hypothesis
- operational changes required

### Scope shaping

- in scope
- out of scope
- MVP
- later-phase ideas

### Assumptions and gaps

- known facts
- assumptions
- risks
- dependencies
- open decisions

### Option analysis

When multiple directions are plausible, compare options with:

- summary
- benefits
- tradeoffs
- delivery impact
- data/integration impact
- recommendation

### Technical thinking without overcommitting

Only when relevant, capture:

- systems touched
- likely integrations
- data entities or reporting needs
- security or compliance concerns
- operational support considerations

### Workshop-ready outputs

When the user is preparing for a session, provide:

- a concise problem framing
- a stakeholder question set
- a decision agenda
- a parking-lot list
- recommended next artifact

## Output patterns

### Quick synthesis

Use for a doc or folder when the user wants a fast first pass.

Suggested structure:

```text
Idea summary

What appears to be true
- ...

What is still assumed
- ...

What needs a decision
- ...

Recommended next step
- ...
```

### Workshop brief

Use when preparing for ideation or discovery.

Suggested sections:

- objective
- participants
- context summary
- key questions
- option areas to explore
- decisions to leave the session with

### Direction recommendation

Use when the user wants a point of view.

Suggested structure:

```text
Recommendation

Why this direction
- ...

Tradeoffs to accept
- ...

What to validate next
- ...
```

## Examples

- **Folder-based ideation:** Read the lightest useful set of discovery docs,
  synthesize the repeated business themes, call out contradictions, and produce
  a workshop-ready brief without pretending the work is implementation-ready.
- **Blank-start ideation:** Start from a rough business problem, separate facts
  from assumptions and open questions, compare a few plausible directions, and
  recommend the next artifact.

## Do Nots

- Do NOT turn ideation into implementation planning unless the user asks
- Do NOT invent certainty where the source material is ambiguous
- Do NOT reopen routine implementation defaults during early ideation
- Do NOT overload the output with templates when a short synthesis is enough
- Do NOT present speculative architecture as a settled decision

## Closed Decisions

- This skill runs before `/plan`; it explores and frames ideas rather than
  planning implementation.
- The default audience is mixed business and technical stakeholders.
- Facts, assumptions, risks, and open questions stay separate.
- The lightest useful output is preferred over a template-heavy deliverable.

## Handoff guidance

At the end, recommend the next best workflow:

- continue ideation
- write or upgrade a BRD/PRD/story
- use `/plan`
- use `/review` later against an implementation artifact
