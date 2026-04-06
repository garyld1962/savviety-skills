---
description: "Review changed code for reuse, quality, and efficiency using 3 parallel reviewer agents, then fix issues found. Run between coding and code review."
argument-hint: "Optional: specific files or areas to focus on"
agents:
  - Code Reuse Reviewer
  - Code Quality Reviewer
  - Efficiency Reviewer
---

# Simplify — Code Cleanup and Refactoring Pass

Auto-refactoring pass that dispatches 3 specialist agents in parallel to review changed code, then fixes the issues they find.

## When to Use

- After finishing a feature or fix, before running code review
- After a batch of changes to clean up structural debt introduced during development
- When code works but feels messy or duplicated

## When NOT to Use

- For correctness or convention compliance — use `#prompt:code-review`
- For cross-model adversarial challenge — use `#prompt:adversarial-review`
- For lint/build/test validation — use `#prompt:checkpoint`

## Recommended Workflow Position

```
coding → #prompt:simplify → #prompt:code-review → #prompt:adversarial-review (optional) → PR
```

## Step 1: Identify Changes

Get the diff to review:

```bash
git diff
git diff --cached
```

If no changes exist, review the most recently discussed or modified files.

Report: "Reviewing N files changed across M packages."

## Step 2: Dispatch Reviewers in Parallel

Send the full diff to all three agents simultaneously:

1. **@Code Reuse Reviewer** — finds duplicated utilities, inline logic that existing helpers handle
2. **@Code Quality Reviewer** — catches redundant state, copy-paste, leaky abstractions, stringly-typed code
3. **@Efficiency Reviewer** — spots unnecessary work, missed concurrency, hot-path bloat, memory concerns

Each agent returns a numbered findings list or confirms the code is clean.

## Step 3: Aggregate Findings

Collect all findings from the three agents. Deduplicate any overlapping issues (same file + same line from multiple agents — keep the more actionable description).

## Step 4: Fix Issues

For each finding:

- **If actionable**: fix it directly in the code. Make the edit.
- **If false positive or not worth addressing**: note it briefly and skip. Do not argue with yourself about borderline cases.
- **If the fix would be risky** (changing public API, altering shared utilities used elsewhere): flag it for the developer instead of auto-fixing.

## Step 5: Summary

After all fixes:

```
## Simplify Results

**Files reviewed:** N
**Issues found:** N (M fixed, K skipped)

### Fixed
- [file:line] Description of what was simplified

### Skipped (not worth the risk / false positive)
- [file:line] Description and why it was skipped

### Code was already clean
(if no issues found)
```

## Key Rules

1. **Fix, don't just report.** This is not a review — it's an auto-refactoring pass. Edit the code.
2. **Minimal changes.** Each fix should be the smallest correct simplification. Don't reorganize the whole file.
3. **Don't break anything.** If a simplification could change behavior, skip it.
4. **Respect existing patterns.** Read `.github/copilot-instructions.md` for project conventions before making changes.
5. **No new features.** Only simplify what exists. Don't add functionality.
6. **Preserve tests.** If tests exist for the simplified code, verify they still pass conceptually. Don't delete test coverage.
