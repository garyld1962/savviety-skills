---
description: "Review changed code for reuse, quality, and efficiency, then fix issues found. Run between coding and code review to clean up before the inspector arrives."
argument-hint: "Optional: specific files or areas to focus on"
---

# Simplify — Code Cleanup and Refactoring Pass

Review all changed files for code reuse opportunities, quality patterns, and efficiency. Fix issues directly — this is an auto-refactoring pass, not a report.

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

## Step 2: Code Reuse Review

For each changed file:

1. **Search for existing utilities and helpers** that could replace newly written code. Look in utility directories, shared modules, and files adjacent to the changed ones.
2. **Flag any new function that duplicates existing functionality.** Suggest the existing function to use instead.
3. **Flag inline logic that could use an existing utility** — hand-rolled string manipulation, manual path handling, custom environment checks, ad-hoc type guards.

## Step 3: Code Quality Review

Review the same changes for structural smells:

1. **Redundant state**: state that duplicates existing state, cached values that could be derived, observers/effects that could be direct calls
2. **Parameter sprawl**: adding new parameters to a function instead of generalizing or restructuring
3. **Copy-paste with slight variation**: near-duplicate code blocks that should be unified with a shared abstraction
4. **Leaky abstractions**: exposing internal details that should be encapsulated, or breaking existing abstraction boundaries
5. **Stringly-typed code**: using raw strings where constants, enums (string unions), or branded types already exist in the codebase
6. **Unnecessary JSX nesting**: wrapper elements that add no layout value — check if inner component props already provide the needed behavior

## Step 4: Efficiency Review

Review the same changes for performance:

1. **Unnecessary work**: redundant computations, repeated file reads, duplicate network/API calls, N+1 patterns
2. **Missed concurrency**: independent operations run sequentially when they could run in parallel (Promise.all, parallel queries)
3. **Hot-path bloat**: new blocking work added to startup or per-request/per-render hot paths
4. **Recurring no-op updates**: state/store updates inside polling loops or event handlers that fire unconditionally — add a change-detection guard so downstream consumers aren't notified when nothing changed
5. **Unnecessary existence checks**: pre-checking file/resource existence before operating (TOCTOU anti-pattern) — operate directly and handle the error
6. **Memory concerns**: unbounded data structures, missing cleanup, event listener leaks
7. **Overly broad operations**: reading entire files when only a portion is needed, loading all items when filtering for one

## Step 5: Fix Issues

For each finding from Steps 2-4:

- **If actionable**: fix it directly in the code. Make the edit.
- **If false positive or not worth addressing**: note it briefly and skip. Do not argue with yourself about borderline cases.
- **If the fix would be risky** (changing public API, altering shared utilities used elsewhere): flag it for the developer instead of auto-fixing.

## Step 6: Summary

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

1. **Fix, don't report.** This is not a review — it's an auto-refactoring pass. Edit the code.
2. **Minimal changes.** Each fix should be the smallest correct simplification. Don't reorganize the whole file.
3. **Don't break anything.** If a simplification could change behavior, skip it.
4. **Respect existing patterns.** Read `.github/copilot-instructions.md` for project conventions before making changes.
5. **No new features.** Only simplify what exists. Don't add functionality.
6. **Preserve tests.** If tests exist for the simplified code, verify they still pass conceptually. Don't delete test coverage.
