---
description: >-
  Explore and shape an idea from a rough ask, a single document, or a folder of
  documents, then deepen it in the requested mode: idea (general option framing),
  ba (business-analysis deepening), or tech (technical solution directions).
argument-hint: '[idea|ba|tech] [topic or document path]'
agent: "agent"
tools:
  - read
  - search
  - edit
  - codebase
---

# Ideate

Use this prompt to start ideation from a rough idea, one document, or a folder of related documents.

Start with a shared ideation pass, then deepen in the selected mode:

- `idea` for general idea shaping and option framing
- `ba` for business-analysis deepening using `.github/skills/ba-ideation/SKILL.md`
- `tech` for technical option framing using `.github/skills/tech-ideation/SKILL.md` without jumping into implementation planning

If no mode is supplied, default to `idea`, then lean toward `ba` when the ask is primarily about business process, stakeholder alignment, requirements direction, or workshop preparation.

Quick examples:

```text
/ideate idea "We need a better enterprise onboarding experience"
/ideate ba @docs/discovery/
/ideate tech @docs/architecture/integration-notes.md
```

## Copilot-native usage

- Parse the first argument as the ideation mode when it matches `idea`, `ba`, or `tech`.
- If the user provides a document, prefer `@file` context or read the exact file.
- If the user provides a folder, inspect the relevant files in that folder and synthesize them instead of treating the folder as one artifact.
- Keep the interaction one question at a time.
- Keep the output light unless the user asks for a deeper workshop pack or decision analysis.
- Do not drift into implementation planning; that belongs in `/plan`.

## Shared starting flow

Always establish the lightest useful version of:

- problem or opportunity
- affected users or stakeholders
- desired outcome
- known facts
- assumptions and risks
- major open questions
- plausible directions

Then branch by mode:

- `idea`: expand the concept, clarify options, and recommend what to validate next
- `ba`: deepen process, scope, decision framing, assumptions, dependencies, and workshop outputs
- `tech`: compare technical directions, systems impacts, data/integration concerns, and architectural tradeoffs without turning the result into an implementation plan

## Output goals

Produce only the lightest useful version of:

- idea summary
- business problem and desired outcome
- known facts, assumptions, risks, and open questions
- scope framing
- option comparison when needed
- workshop-ready questions or agenda when useful
- recommended next step

### BA mode additions

- current/future state, process friction, operational changes
- workshop-ready: problem framing, stakeholder question set, decision agenda, parking lot

### Tech mode additions

- systems touched, ownership boundaries, affected interfaces
- data flows, source-of-truth concerns, integration patterns
- major technical risks, spikes or experiments worth running
- technical workshop brief: objective, systems in play, decision areas

## CRITICAL: Do Not Guess

- Do NOT invent certainty that is not supported by the source material or user input.
- Do NOT read every file in a folder if a smaller set can establish the pattern and gaps.
- Do NOT force technical implementation details during early ideation unless they materially change the business decision.
- Do NOT turn routine implementation defaults into workshop decisions.
- Do NOT jump into `/plan` until the direction is clear enough to plan.
- Do NOT lose the shared ideation context when moving from `idea` into a deeper mode such as `ba` or `tech`.

## Built-in-first rule

- Use this prompt to shape the idea and decide what needs to be true.
- Use `/plan` after the direction is chosen and the work is ready for implementation planning.
- Use `/review` later to challenge an implementation, not the initial ideation.
