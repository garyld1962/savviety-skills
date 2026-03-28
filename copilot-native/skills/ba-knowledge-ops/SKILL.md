---
name: ba-knowledge-ops
description: Templates and quality checks for capturing BA knowledge and evaluating AI-generated BA deliverables.
---

# BA Knowledge Operations

Use this skill for two adjacent workflows:

- `#prompt:ba-knowledge-capture`
- `#prompt:ba-eval-harness`

## Relationship to Copilot built-ins

- Use this skill to make BA knowledge durable and reusable across sessions.
- Use `/plan` only after the captured decisions or evaluated deliverables are
  ready to drive execution work.
- Use `@file` context to bring saved outputs back into later Copilot CLI runs.

## Knowledge capture templates

Match the user intent to the lightest fitting template:

1. Decision capture
2. Stakeholder intelligence
3. Requirements insight
4. Process observation
5. Meeting debrief
6. Lessons learned
7. Business rule discovery
8. AI session save

For each template:

- capture only what the user tells you
- ask for missing fields selectively
- keep the result concise and searchable

## Eval harness design

When building a BA evaluation suite:

- inventory the deliverables the user most often drafts with AI
- identify the deliverables where quality most affects credibility
- create repeatable pass/partial/fail criteria
- include BA-specific failure modes such as hallucinated facts, vague
  requirements, missing stakeholder perspectives, and untestable acceptance
  criteria

## Eval output contract

Each test case should include:

- Deliverable name
- Sample task
- Evaluation criteria
- Known AI failure modes
- Scoring rubric
- Result log template

## Guardrails

- Quality criteria must be observable, not aspirational.
- Do not invent sample tasks or org standards.
- If one input spans multiple capture templates, suggest splitting it.
