---
description: "Execute a written implementation plan end-to-end with per-task build/test cycles, quick code review per task, full review at the end, and a final acceptance gate."
argument-hint: "Path to plan file (optional)..."
---

# Execute Plan — Implementation Plan Executor

Execute a written implementation plan end-to-end with per-task build/test cycles and a final acceptance gate.

## When to Use

- You have a validated plan file in `docs/plans/` and want to implement it
- After running the `plan` skill to create a plan

## Arguments

- `<path>` — path to the plan file (optional; if omitted, finds most recent file in `docs/plans/`)

## Phase 1: Load Plan

1. **Find the plan file:**
   - If a path argument was provided, read that file.
   - Otherwise, find the most recent `.md` file in `docs/plans/`.
   - If no plan file found, stop: "No plan file found."

2. **Parse the plan** into an ordered task list.

3. **Report:** "Found N tasks in <plan-file>. Starting execution."

## Phase 2: Per-Task Loop

For each task in order:

#### 2a. Read Requirements
Read the task description from the plan.

#### 2b. Implement
Follow the plan exactly. Do not add unplanned features or refactors.

#### 2c. Build
```bash
pnpm -r build
```
If build fails: diagnose, fix, retry (max 3 attempts). If still failing, stop and report.

#### 2d. Test
```bash
pnpm --filter <package-name> test -- --run
```
If tests fail: diagnose, fix, retry (max 3 attempts). If still failing, stop and report.

#### 2e. Quick Review
Apply typescript-quality and security specialists against files changed in this task. Auto-fix Blocker/High findings. Skip Medium/Low/Info.

#### 2f. Commit
```
<type>(<scope>): <description>

Task N from <plan-file>
```

#### 2g. Report
```
Task N/M: DONE — <brief summary>
  Files: <list>
  Commit: <sha>
```

## Phase 3: Acceptance Gate

After all tasks complete:

#### 3a. Full Code Review
Apply all code review specialists against cumulative changeset (`git diff origin/main --name-only`). Auto-fix Blocker/High (max 3 cycles). Record Medium/Low/Info.

> **Auto-fix process:** (1) Identify the fix, (2) Apply changes, (3) Build and test, (4) Commit with `fix: address <finding title>`, (5) Re-run review to confirm. If a Blocker cannot be auto-fixed after 3 cycles, escalate to ABORT.

#### 3b. Plan Alignment Check
1. Re-read the original plan file
2. Compare against cumulative diff
3. Verify: **Completeness**, **Scope**, **Accuracy**, **Deviations**

#### 3c. Run Checkpoint
Run the checkpoint quality gate (lint, build, test).

#### 3d. Calculate Verdict
- **PASS**: All tasks done, no Blocker/High remain, checkpoint passes, plan alignment clean.
- **WARN**: All tasks done, only Medium/Low remain, checkpoint passes.
- **FAIL**: Any Blocker/High remain, checkpoint fails, or plan alignment has gaps.
- **ABORT**: A Blocker is system-breaking and cannot be auto-fixed.

## Phase 4: Report

```
## Execution Report

**Plan:** <plan-file>
**Tasks:** N/N completed

### Per-Task Summary
| # | Description | Commit | Files Changed | Status |
|---|-------------|--------|---------------|--------|

### Code Review Findings
- Blocker: N (N auto-fixed)
- High: N (N auto-fixed)
- Medium: N
- Low: N
- Info: N

### Plan Alignment
- All tasks implemented: YES/NO
- Unplanned changes: NONE / [list]
- Spec deviations: NONE / [list]

### Checkpoint
- Lint: PASS/FAIL
- Build: PASS/FAIL
- Tests: PASS/FAIL

### Verdict: PASS / WARN / FAIL / ABORT
```

## Key Rules

- **Follow the plan exactly.** Do not add unplanned features, refactors, or "improvements."
- **Stop on persistent failure.** After 3 retries on build or test, stop and report.
- **Quick review is fast, full review is thorough.** Per-task uses only typescript-quality + security. Acceptance gate uses all specialists.
- **Commits reference the plan.** Every commit message ties back to the task number and plan file.
