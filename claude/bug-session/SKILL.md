---
name: bug-session
description: "Interactive bug-reporting session: user describes problems conversationally, agent explores the codebase for domain context, and files durable GitHub issues. Use when user wants to report bugs, do QA testing, capture defects — phrases like 'let's do a bug session', 'I found some issues', 'QA session', 'help me file these bugs'. When NOT to Use: single known bug to investigate (use /triage); existing issue to fix (use /hotfix or /execute-prd)."
---

# /bug-session -- Conversational Bug Capture

**Purpose:** Run an interactive session where the user describes bugs in plain language. For each issue, ask minimal clarifying questions, explore the codebase in the background for domain context, then file a durable GitHub issue. Issues are written to survive refactors — no file paths, no internal module names.

## When to Use

- User wants to report multiple bugs they've found
- Running QA on a feature before shipping
- Capturing defects from manual testing
- Handing off bugs from user testing into GitHub

## When NOT to Use

- One known bug that needs investigation — use `/triage`
- Already have a GitHub issue and need to fix it — use `/hotfix` or `/execute-prd`

## Per-Issue Workflow

### 1. Listen

Let the user describe the problem in their own words. Don't interrupt or ask anything yet.

### 2. Clarify (max 2-3 questions)

Ask only what's needed to file a good issue:
- What did you expect vs what actually happened?
- Steps to reproduce, if not obvious
- Consistent or intermittent?

If the description is clear enough to file, skip the questions and move on.

### 3. Explore in Background

While talking, spawn an Explore sub-agent to:
- Read `UBIQUITOUS_LANGUAGE.md` if it exists
- Find the feature area in the codebase
- Learn the domain terms used there

**Goal:** Write a better issue — not find a fix. The filed issue must NOT reference specific files, line numbers, or internal module names. Those rot after the next refactor.

### 4. Single Issue or Breakdown?

Decide before filing.

**Break down** when:
- The fix spans multiple independent areas
- Different people could reasonably work on separate parts
- There are distinct failure modes with different root causes

**Keep single** when:
- One behavior is wrong in one place
- All symptoms trace to the same root cause

When breaking down: create issues in dependency order (blockers first) so you can reference real issue numbers.

### 5. File the Issue

Use `gh issue create`. Don't ask the user to review first — file and share the URL.

```markdown
## What happened
[Actual behavior the user experienced, plain language]

## What I expected
[Expected behavior]

## Steps to reproduce
1. [Concrete numbered steps]
2. [Use domain terms, not internal module names]
3. [Include relevant inputs, flags, or config]

## Additional context
[Observations that help frame it — domain language only, no file paths]
```

## Session Flow

Repeat the per-issue workflow until the user says they're done. At the end, share all filed issue URLs as a list.
