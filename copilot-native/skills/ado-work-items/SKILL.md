---
name: ado-work-items
description: Retrieval and normalization workflow for Azure DevOps work items used as planning or implementation inputs.
---

# ADO Work Items

Use this skill to fetch and summarize Azure DevOps work items.

## Relationship to Copilot built-ins

- Use this custom workflow because Copilot has no built-in Azure DevOps work
  item retriever.
- Use the resulting work item details as input to `prd-validator`, BA prompts,
  or built-in `/plan`.

## Retrieval contract

- resolve organization and project configuration first
- prefer existing local configuration over guessing
- fetch the work item by ID
- extract the title, description, acceptance criteria, state, assignee, tags,
  and hierarchy when available
- convert HTML-heavy fields into readable text without inventing meaning

## Optional enrichment

- fetch comments or expanded relations only when the user asks
- note missing fields explicitly instead of hiding them

## Guardrails

- Do not guess organization or project defaults.
- Do not treat unavailable CLI tooling as success.
- Do not rewrite the work item into a spec unless the user asks for that next
  step.
