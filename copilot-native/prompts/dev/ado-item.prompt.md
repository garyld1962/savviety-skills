---
description: >-
  Retrieve an Azure DevOps work item by ID and normalize its key fields for use
  in planning, BA, or implementation workflows.
argument-hint: '[work item ID]'
agent: 'agent'
tools:
  - execute
  - read
  - search
---

# ADO Item

Use this prompt when a work item in Azure DevOps is the input artifact for the
next step.

Follow the skill: `.github/skills/ado-work-items/SKILL.md`

## Copilot-native usage

- Resolve org and project config before fetching.
- Use the retrieved item as input to `prd-validator`, BA prompts, or built-in
  `/plan`.
