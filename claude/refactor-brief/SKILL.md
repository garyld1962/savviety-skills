---
name: refactor-brief
description: "Plan a refactor through structured interview, then file it as a GitHub issue RFC with a tiny-commit sequence and decision record. Use when user wants to plan a refactor before implementing — phrases like 'plan a refactor', 'create a refactor issue', 'refactor RFC', 'break this refactor into safe steps'. When NOT to Use: refactor already planned and ready to execute (use /execute-plan); quick code cleanup (use /simplify); feature work disguised as a refactor (use /prd-validate first)."
---

# /refactor-brief -- Refactor Interview → RFC Issue

**Purpose:** Interview the user about a proposed refactor, verify their assertions against the codebase, hammer out scope, and produce a GitHub issue RFC with a tiny-commit implementation plan. Based on Martin Fowler's principle: "make each refactoring step as small as possible so the program is always working."

## When to Use

- Planning a non-trivial refactor before implementation starts
- Creating a shareable RFC that others can review or pick up
- Breaking a large change into safe, independently-reviewable steps

## When NOT to Use

- The refactor is already planned — use `/execute-plan`
- A quick cleanup — just do it with `/simplify`
- A feature change dressed up as a refactor — use `/prd-validate` first

## Workflow

### 1. Problem Description

Ask the user to describe in detail:
- What problem are you solving?
- What does the codebase look like now?
- What should it look like after the refactor?
- Any ideas on approach already?

### 2. Verify Against the Codebase

Explore the repo to confirm their assertions:
- Does the problem they describe actually exist as described?
- What test coverage exists in this area?
- Are there similar patterns elsewhere the refactor should follow?
- What callers depend on the interfaces being changed?

### 3. Surface Alternatives

Before locking in the approach:
- Is there a simpler way to achieve the same goal?
- Is there an incremental path that avoids a big-bang change?
- Raise anything the user may not have considered

### 4. Interview on Scope

Work through each decision:
- What exactly changes? What explicitly does NOT change?
- What interface contracts stay stable for callers?
- Any schema changes, API contracts, or event shapes?
- If test coverage is thin, ask what the testing plan is before proceeding

### 5. Tiny Commit Sequence

Draft the commit sequence. Each commit must:
- Leave the codebase in a working state
- Be as small as possible while still being meaningful
- Be describable in one sentence of present-tense imperative

Order: data migrations before logic, interface changes before implementations, tests before behavior changes.

### 6. File the GitHub Issue

Use `gh issue create` with this template:

```markdown
## Problem Statement
[The problem from the developer's perspective]

## Solution
[The proposed solution from the developer's perspective]

## Commit Sequence
[Detailed tiny-commit plan. Plain English. No file paths or code snippets — those become stale. Each commit leaves code in a working state.]

## Decision Record
- Modules affected:
- Interface changes:
- Architectural decisions:
- Schema changes (if any):
- API contracts (if any):
- Explicitly out of scope:

## Testing Decisions
- What makes a good test here (external behavior, not implementation details):
- Which modules will have tests:
- Prior art — similar test patterns to follow in this codebase:

## Out of Scope
[What this refactor deliberately does not address]

## Further Notes
[Optional]
```
