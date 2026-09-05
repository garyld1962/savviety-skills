---
name: issue-slices
description: 'Break a PRD into independently-grabbable GitHub issues as vertical tracer-bullet
  slices. Use when user wants to convert a PRD to tickets, create implementation issues
  from a PRD — phrases like ''break this PRD into issues'', ''create tickets from
  the PRD'', ''slice the PRD into work items''. When NOT to Use: want the PRD executed
  end-to-end automatically (use /execute-prd); rough idea not yet a PRD (use /goal
  → /prd-create first); want a plan doc not issues (use /execute-prd step 1).'
whenToUse: 'Break a PRD into independently-grabbable GitHub issues as vertical tracer-bullet
  slices. Use when user wants to convert a PRD to tickets, create implementation issues
  from a PRD — phrases like ''break this PRD into issues'', ''create tickets from
  the PRD'', ''slice the PRD into work items''. When NOT to Use: want the PRD executed
  end-to-end automatically (use /execute-prd); rough idea not yet a PRD (use /goal
  → /prd-create first); want a plan doc not issues (use /execute-prd step 1).'
---


# /skill:issue-slices -- PRD → Vertical Slice Issues

**Purpose:** Decompose a PRD into independently-grabbable GitHub issues, each a thin vertical slice through all integration layers. Uses the tracer-bullet methodology: every issue is demonstrable on its own, not a horizontal cut through one layer.

## When to Use

- A PRD is ready and needs to be broken into implementation tickets
- You want human-pickable issues before automated execution
- The PRD is too large to execute in one pass

## When NOT to Use

- You want the full PRD executed end-to-end automatically — use `/skill:execute-prd`
- The input is a rough idea, not a PRD — use `/skill:prd-create` first
- You want a plan doc rather than issues — use `/skill:execute-prd` step 1

## Workflow

### 1. Locate the PRD

Ask for the PRD GitHub issue number or URL.

Fetch it:
```bash
gh issue view <number>
```

### 2. Explore the Codebase

Read the relevant area to understand:
- Current state of the code
- Existing patterns and conventions the issues should follow
- Where each slice will land across the layers

### 3. Draft Vertical Slices

Each issue is a **tracer bullet**: a thin slice through ALL layers (schema, API, UI, tests), not one layer across the whole feature.

Rules:
- Each slice is independently demonstrable or verifiable once complete
- Prefer many thin slices over few thick ones
- Each slice is safe to implement and merge without breaking others

Classify each as **HITL** (requires human decision or review mid-slice) or **AFK** (agent-executable without human involvement). Prefer AFK.

### 4. Review With User

Present as a numbered list. For each slice show:
- **Title** — short descriptive name
- **Type** — HITL / AFK
- **Blocked by** — which slices must complete first (none if independent)
- **User stories covered** — which PRD requirements this addresses

Ask:
- Granularity right? Too coarse or too fine?
- Dependencies correct?
- HITL/AFK classifications accurate?

Iterate until the user approves the full breakdown.

### 5. Create the Issues

Create in dependency order (blockers first — so you can reference real issue numbers in later issues).

Use `gh issue create` with this template:

```markdown
## Parent PRD
#<prd-issue-number>

## What to Build
[End-to-end behavior of this slice. Reference the parent PRD rather than duplicating content. Describe what it does, not how it's implemented layer by layer.]

## Acceptance Criteria
- [ ] 
- [ ] 
- [ ] 

## Blocked By
[#<issue-number> — reason]  or  "None — can start immediately"

## User Stories Addressed
[Reference by title or number from the parent PRD]
```

Do NOT close or modify the parent PRD issue.
