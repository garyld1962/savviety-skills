---
description: >-
  Retrieve a work item from Azure DevOps OR Linear by ID and normalize its key
  fields for use in planning, BA, or implementation workflows.
argument-hint: '[ADO-ID or LINEAR-ID (e.g. ENG-123)]'
agent: 'agent'
tools:
  - execute
  - read
  - search
---

# Work Item

Use this prompt when a work item is the input artifact for the next step.

## Tracker detection

Determine the tracker from the ID format:

- **Linear** — team-prefix format: `ENG-123`, `INF-456`, `PLT-7` (letters,
  hyphen, digits)
- **ADO** — numeric only: `12345`

If the format is ambiguous, ask the user which tracker to use.

## Linear path

When the ID matches the Linear format:

1. Call `mcp__plugin_linear_linear__get_issue` with the issue ID (e.g.
   `ENG-123`).
2. Extract from the response:
   - **Title** — `title`
   - **Description / acceptance criteria** — `description` (markdown)
   - **Status** — `state.name`
   - **Assignee** — `assignee.name` (or "Unassigned")
   - **Labels** — `labels[].name` (or none)
   - **URL** — `url`
3. Note any missing fields explicitly; do not infer them.
4. Present the normalized output (see format below), then offer to hand off to
   `prd-validate`, BA prompts, or built-in `/plan`.

## ADO path

When the ID is numeric:

Follow the skill: `.github/skills/ado-work-items/SKILL.md`

- Resolve org and project config before fetching.
- Use the retrieved item as input to `prd-validate`, BA prompts, or built-in
  `/plan`.

## Normalized output format

Present the result using this structure regardless of tracker:

```
**Title:** <title>
**Status:** <status>
**Assignee:** <assignee or "Unassigned">
**Labels/Tags:** <comma-separated or "none">
**URL:** <url>

**Description / Acceptance Criteria:**
<description text>
```
