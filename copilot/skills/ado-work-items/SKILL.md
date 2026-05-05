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

## Examples

- **Planning input:** Fetch work item `12345`, normalize the title,
  description, acceptance criteria, state, and tags, then hand the result to
  `prd-validator` or `/plan`.
- **Missing fields:** If the work item has no acceptance criteria or assignee,
  report those fields as missing instead of filling them in from context clues.

## Guardrails

- Do not guess organization or project defaults.
- Do not treat unavailable CLI tooling as success.
- Do not rewrite the work item into a spec unless the user asks for that next
  step.

## Do Nots

- Do not silently drop HTML-heavy field content that can be converted into
  readable text.
- Do not fetch comments, links, or expanded hierarchy unless the user asked for
  that extra scope.

## Closed Decisions

- Existing local configuration is authoritative over guessed org or project
  defaults.
- This skill retrieves and normalizes work items; it does not automatically
  convert them into an AERS or implementation plan.
- Missing data must stay visibly missing rather than being inferred.
