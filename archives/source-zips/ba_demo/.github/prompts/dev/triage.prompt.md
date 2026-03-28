---
description: "Investigate a bug report: reproduce, gather diagnostics, identify root cause, and determine fix scope. Outputs a triage report that feeds into the plan skill."
argument-hint: "Describe the bug, paste an error, or provide an ADO item ID..."
---

# Bug Triage — Investigation & Root Cause Analysis

Investigate a bug report from reproduction through root cause identification. Produces a structured summary ready for the `plan` skill.

## When to Use

- A bug is reported and you need to understand it before fixing
- You have a stack trace or error message and need to find the source
- Something broke and you don't know why yet

## Arguments

- `<description>` — bug description, error message, or symptoms
- `--ado <item-id>` — fetch bug details from an ADO work item
- `--quick` — skip git bisect and regression analysis (for obvious bugs)

---

## Phase 1: Gather Context

### 1.1 Parse the Report
Extract: symptoms, steps to reproduce, expected vs actual, environment, frequency.

If `--ado <item-id>`: fetch via `az boards work-item show --id <ITEM_ID> --output json`.

### 1.2 Search for Related Context
```bash
# Search for error text in codebase
grep -r "<error message>" --include="*.ts" --include="*.tsx" -l

# Check recent commits
git log --oneline --since="2 weeks ago" --all -- <suspected paths>

# Check related issues/PRs
gh pr list --search "<keywords>" --state all --limit 10
gh issue list --search "<keywords>" --state all --limit 10
```

### 1.3 Read Affected Code
Files containing error text, tests covering the area, recent changes.

---

## Phase 2: Reproduce

### 2.1 Write a Reproduction Test
If possible, write a minimal failing test.

### 2.2 Verify Reproduction
Test fails as expected → confirmed. Test passes → refine and retry.

---

## Phase 3: Root Cause Analysis

### 3.1 Trace the Code Path
From the error site, trace backward: where does it originate? What inputs? Where do they come from? What assumption is violated?

### 3.2 Regression Check (unless --quick)
```bash
git log --oneline --all -- <affected files> | head -20
git show <suspect-sha> -- <affected files>
```

### 3.3 Classify the Root Cause

| Category | Examples |
|----------|---------|
| **Logic error** | Wrong condition, off-by-one, missing case |
| **Type error** | Null/undefined not handled, wrong type assumption |
| **Integration** | API contract changed, dependency broke something |
| **Race condition** | Timing-dependent, async ordering, missing await |
| **Config/env** | Wrong env var, missing config, path issue |
| **Data** | Corrupt input, edge case data, encoding issue |

---

## Phase 4: Scope the Fix

### 4.1 Identify Files to Change
Root cause files, test files, related files with same pattern.

### 4.2 Assess Risk

| Factor | Assessment |
|--------|-----------|
| Blast radius | How many features/users affected? |
| Fix complexity | One-line vs. structural change? |
| Regression risk | Could the fix break something else? |
| Test coverage | Is the area well-tested? |

### 4.3 Recommend Approach
- **Simple fix**: Proceed to `plan --type bug`
- **Complex fix**: Full plan with multiple tasks
- **Hotfix**: If production is broken, use the `hotfix` skill

---

## Phase 5: Report

```markdown
## Triage Report

**Bug:** <one-line summary>
**Source:** ADO #<ID> (if applicable)
**Severity:** Critical / High / Medium / Low
**Reproduced:** YES / NO / MANUAL-ONLY

### Symptoms
<what the user sees>

### Root Cause
<clear explanation>
**Category:** <classification>
**Introduced by:** <commit sha> — <message> (if identified)

### Affected Files
| File | Role |
|------|------|
| `path/to/file.ts` | Root cause |

### Fix Scope
- **Complexity:** Simple / Medium / Complex
- **Blast radius:** <assessment>
- **Regression risk:** <assessment>
- **Recommended approach:** plan --type bug / hotfix
```

Offer: **"Plan the fix"** → hand off to plan, **"Hotfix now"** → hotfix skill, **"Need more info"** → continue.

## Key Rules

- **Investigate first, fix later.** This skill does NOT write fixes.
- **Show your work.** Every conclusion needs evidence.
- **Don't guess.** If you can't identify root cause, say so.
- **Reproduction is mandatory.** A bug without a repro is not triaged.
