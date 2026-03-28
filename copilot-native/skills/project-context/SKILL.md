---
name: project-context
description: Structured interview and document shape for building a reusable BA project context artifact for Copilot sessions.
---

# Project Context

Use this skill when creating a reusable project context document for BA work or
other prompt-driven collaboration.

## Relationship to Copilot built-ins

- Use this skill before `/plan` when the main problem is missing business or
  organizational context rather than missing implementation detail.
- Use `@file` references to reuse the resulting context document in later
  Copilot CLI sessions.
- This skill creates durable project context. It does not replace execution
  planning or implementation review.

## Interview domains

Capture only what the user actually knows across these domains:

1. Project overview
2. Stakeholders and audiences
3. Business context and domain
4. Domain terminology
5. Requirements context
6. Constraints and boundaries
7. Quality standards and preferences
8. AI interaction rules

Ask in small groups and avoid repeating information the user already provided.

## Output contract

Produce a concise, reusable context artifact with these sections:

- Project
- Phase
- Project Overview
- Stakeholder Map
- Business Context
- Domain Terminology
- Scope Boundaries
- Constraints
- Political and Organizational Context
- Deliverable Standards
- AI Session Rules
- When In Doubt

## Guardrails

- Include only user-provided facts.
- Use explicit placeholders like `[TO FILL: ...]` instead of inventing content.
- Compress answers into token-efficient reference notes.
- Surface political or organizational risks directly when the user mentions them.
