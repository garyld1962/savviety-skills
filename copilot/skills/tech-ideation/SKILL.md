---
name: tech-ideation
description: Explore technical solution directions from a rough idea, a single document, or a folder of documents by clarifying constraints, systems impact, architectural options, data and integration implications, and recommended next validation steps without turning the work into implementation planning.
---

# Tech Ideation

Use this skill to shape technical directions before implementation planning.

## Relationship to Copilot built-ins

- Use this skill before `/plan`
- Use this skill when the user wants to compare technical directions, integration patterns, architecture options, or delivery tradeoffs
- Use `/plan` after a technical direction is chosen and the work is ready for implementation planning
- Use `@file` context for a specific document and exact repo inspection for a folder of docs

## Relationship to `/ideate` modes

Treat this skill as the specialist branch for `/ideate tech`.

Expected flow:

1. shared ideation establishes the problem, users, desired outcome, and major uncertainties
2. tech ideation deepens technical constraints, systems impact, data and integration concerns, and architectural tradeoffs
3. the handoff recommends what to validate next and whether the work is ready for `/plan`

If `/ideate` is called without a mode and the ask is primarily system-facing or architecture-facing, this skill is a good follow-on after the shared ideation pass.

Quick invocation examples:

```text
/ideate tech @docs/architecture/
/ideate tech @notes/api-options.md
/ideate tech "Compare options for event-driven vs synchronous integration for partner notifications"
```

## Entry modes

### Single document

Use when the user provides one artifact such as:

- architecture notes
- integration proposal
- system overview
- technical spike notes
- API notes
- design discussion memo

Goal: extract what the source implies technically, surface important tradeoffs, and frame the next validation steps without pretending the direction is already implementation-ready.

### Folder of documents

Use when the user provides a folder path with multiple related artifacts.

Goal:

- identify the most relevant technical artifacts
- synthesize repeated constraints and patterns
- surface contradictions
- compare plausible technical directions

When working from a folder, prefer the lightest useful read set and name which files drove the conclusions.

### Blank start

Use when the user has only a rough technical idea.

Opening prompt:

```text
Tell me the technical idea or problem in plain language. You can describe the system change, integration, architecture concern, or delivery challenge roughly and I will help shape the options.
```

## Audience

Default to mixed technical and business stakeholders.

Translate between:

- business need and technical consequence
- system tradeoffs and delivery impact
- architecture choices and operational cost or risk

## Interaction rules

- Ask one question at a time
- Prefer multiple-choice with a recommended default when practical
- Start with high-leverage uncertainty, not implementation detail
- Distinguish facts, assumptions, constraints, risks, and open decisions
- If the user says "you choose," propose a default and explain the tradeoff briefly

## What to produce

Produce only the lightest useful set for the situation.

### Technical framing

- problem statement
- desired technical outcome
- key constraints
- major quality attributes

### System impact

- systems touched
- ownership boundaries
- affected interfaces
- deployment or operational implications

### Data and integration thinking

- likely entities or data flows
- source-of-truth concerns
- external dependencies
- integration patterns and failure modes

### Option analysis

When multiple directions are plausible, compare options with:

- summary
- benefits
- tradeoffs
- implementation complexity
- operational impact
- security/compliance impact when relevant
- recommendation

### Risk and validation

- major technical risks
- assumptions to prove
- spikes or experiments worth running
- observability or operability concerns

### Workshop-ready outputs

When the user is preparing for a session, provide:

- a concise technical framing
- a decision agenda
- option comparison topics
- technical questions for stakeholders or engineers
- recommended next artifact

## Output patterns

### Quick synthesis

Use for a doc or folder when the user wants a fast first pass.

Suggested structure:

```text
Technical direction summary

What appears to be true
- ...

Key constraints
- ...

Technical options
- ...

What to validate next
- ...
```

### Option comparison

Suggested sections:

- option
- when it fits
- tradeoffs
- risks
- recommended direction

### Technical workshop brief

Suggested sections:

- objective
- systems in play
- decision areas
- questions to resolve
- outputs to leave the session with

## Examples

- **Architecture comparison:** Compare event-driven and synchronous integration
  options, surface tradeoffs and failure modes, and recommend what to validate
  next without choosing implementation details prematurely.
- **Folder-based technical synthesis:** Read the lightest useful architecture
  docs, summarize the repeated technical constraints, identify contradictions,
  and produce a concise option brief.

## Do Nots

- Do NOT turn ideation into implementation planning unless the user asks
- Do NOT invent architecture certainty where the source material is ambiguous
- Do NOT present speculative technical direction as a settled design
- Do NOT force low-value implementation defaults into technical decision making
- Do NOT overload the output with diagrams or templates when a concise comparison is enough

## Closed Decisions

- This skill runs before `/plan`; it shapes technical direction rather than
  implementation sequencing.
- Facts, assumptions, constraints, risks, and open decisions remain distinct.
- The default audience is mixed technical and business stakeholders.
- Prefer the lightest useful comparison over heavyweight design artifacts unless
  the user explicitly wants them.

## Handoff guidance

At the end, recommend the next best workflow:

- continue ideation
- write or upgrade a technical design note, BRD/PRD/story, or spike brief
- use `/plan`
- use `/review` later against an implementation artifact
