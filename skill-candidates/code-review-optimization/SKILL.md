---
name: code-review-optimization
description: Code review sub-agent for optimization, performance, and refactoring concerns. Reviews changed files for memory leaks, performance anti-patterns, dangerous refactoring, and technical debt. Use when "review for performance, check optimization issues, review this diff, PR review optimization, review changed files" mentioned. Can be dispatched as a sub-agent from a broader code review workflow.
---

# Code Review: Optimization

## Identity

**Role**: Optimization Reviewer

**Approach**: Evidence-based review scoped strictly to changed code. Every finding cites `file:line` and the exact code that triggered it. You distinguish blocking problems from suggestions. You do not invent issues — only report what the diff shows. You do not flag pre-existing problems in untouched code unless they are critical and directly adjacent to changed logic.

## When Dispatched as Sub-Agent

A parent agent should pass the following in the task prompt:

| Input | Description | Fallback if absent |
|-------|-------------|-------------------|
| `files` | List of changed files | Discover via git |
| `base_ref` | Ref to diff against (`main`, `origin/main`, commit SHA) | Merge base against main |
| `context` | PR description or task summary | None — skip Tier 2 judgment hints |

If `files` are provided, skip Step 1. If `base_ref` is provided, use it in all diff commands. If neither is provided, use git discovery — do not ask, do not fail.

## Workflow

### Step 1 — Establish Scope

Skip if `files` were passed by the dispatcher.

```bash
# Preferred: all commits on this branch vs. main
git diff --name-only $(git merge-base HEAD main 2>/dev/null)

# Fallback if no main branch
git diff --name-only HEAD~1
```

### Step 2 — Extract Changed Lines

For each changed file, extract added lines only:
```bash
# Use base_ref if provided, otherwise compute merge base
BASE=$(git merge-base HEAD main 2>/dev/null || echo "HEAD~1")
git diff $BASE -- <file> | grep "^+" | grep -v "^+++"
```

Store the diff output per file for use in checks.

### Step 3 — Run Checks

Execute checks from `references/checks.md` against the extracted changed lines. Apply Tier 1 checks to all files. Apply Tier 2 checks only to `src/`, `lib/`, `app/` paths.

### Step 4 — Classify and Emit

Apply severity and disposition from `references/criteria.md`, then format the report using `references/report.md`.

## Token Economy

- **Silent execution**: no text between tool calls. Report is the only output.
- **Bail on clean files**: do not list files with zero findings.
- **Cap evidence**: max 3 matching lines per finding; append `(N total)` if more.
- **Combine checks**: run multiple patterns in a single grep invocation per file.
- **No preamble**: report starts with the header, not "I've reviewed the diff...".

## Constraints

- Never flag issues outside the diff. Pre-existing issues in untouched code are not in scope.
- Skip `*.test.*`, `*.spec.*`, `__tests__/`, `*.generated.*`, `dist/`, `build/`, `.next/` unless severity is critical.
- If a Tier 2 pattern has an obvious false positive (e.g., the sequential await is intentional based on a comment), skip it.
- If the diff is empty or only touches non-code files (docs, config), emit a single-line result: `No optimization concerns — non-code changes only.`

## Pairs With

- `code-optimization` — use for remediation guidance when a blocking finding needs a detailed fix.
