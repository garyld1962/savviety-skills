---
description: >-
  Execute a written implementation plan end-to-end with per-task build/test
  cycles, quick code review per task, full review at the end, and acceptance
  gate.
argument-hint: '[path/to/plan.md]'
agent: 'agent'
tools:
  - execute
  - read
  - search
  - codebase
  - edit
---

# Execute Plan — Implementation Plan Executor

Execute a written implementation plan end-to-end with per-task build/test cycles and a final acceptance gate.

## When to Use

- You have a validated plan file in `docs/plans/` and want to implement it
- After running the `plan` prompt to create a plan

## Arguments

- `<path>` — path to the plan file (optional; if omitted, finds most recent in `docs/plans/`)

---

## CRITICAL: Do Not Guess

- **Plan file location**: If no path is provided, search `docs/plans/` for the most recent file. Do NOT assume a filename.
- **Build/test commands**: Read `package.json` scripts or project docs to find the correct commands. Do NOT assume `pnpm -r build` or `pnpm vitest`.
- **Package names**: When running filtered test commands, use the ACTUAL package name from `package.json`, not the directory name.
- **Plan interpretation**: Follow the plan LITERALLY. If a step says "create file X with content Y," create exactly that. Do NOT improve, optimize, or "enhance" the plan.
- **Import paths**: Copy imports from the plan if provided. If not provided, READ existing files to find the correct import patterns. Do NOT guess.

---

## Phase 1: Load Plan

### 1a. Find the plan file

```bash
# If path provided, verify it exists
ls <provided-path>

# If no path, find most recent plan
ls -t docs/plans/*.md 2>/dev/null | head -1
```

If no plan file found: **STOP** with "No plan file found. Provide a path or create a plan in `docs/plans/`."

### 1b. Parse the plan

Read the file and extract an ordered task list. Tasks are typically:
- Numbered sections (`### Task 1:`, `### Task 2:`)
- Headings with steps underneath
- Checklist items

### 1c. Detect project tooling

**Before starting any implementation**, discover the correct commands:

```bash
# Package manager
ls pnpm-lock.yaml package-lock.json yarn.lock bun.lock 2>/dev/null

# Build command
cat package.json | grep '"build"'

# Test command
cat package.json | grep '"test"'

# Lint command (optional)
cat package.json | grep '"lint"'
```

### 1d. Report

```
Plan: <plan-file>
Tasks: N
Build command: <detected>
Test command: <detected>

Starting execution...
```

---

## Phase 2: Per-Task Loop

For each task in order:

### 2a. Read Requirements

Read the task description from the plan. Understand:
- What files to create or modify (exact paths from the plan)
- What behavior is expected
- What depends on this task

### 2b. Implement

Follow the plan EXACTLY. Create/modify files as specified.

**Do NOT:**
- Add unplanned features or refactors
- "Improve" the code beyond what the plan specifies
- Change the architecture or approach
- Skip steps because "they seem unnecessary"

**If the plan has an error** (wrong path, missing import, syntax issue): Fix the error minimally and note the deviation. Do NOT use the error as an excuse to redesign.

### 2c. Build

Run the detected build command:

```bash
<detected-build-command>
```

### Example: Correct

```bash
# Detected from package.json scripts.build
pnpm -r build
```

### Example: INCORRECT

```bash
# WRONG: Guessing the build command
tsc   # ← Project might use a different build tool
```

If build fails:
1. Read the error message carefully
2. Diagnose the root cause (missing import? type error? syntax?)
3. Fix the minimal change needed
4. Retry (max 3 attempts)
5. If still failing after 3: **STOP** and report the build failure

### 2d. Test

Run tests for the changed package:

```bash
<detected-test-command> --filter <actual-package-name>
```

**Get the actual package name:**

```bash
# Read the package.json in the changed directory
cat <changed-dir>/package.json | grep '"name"'
```

Do NOT assume the package name matches the directory name.

If tests fail:
1. Read the failure output
2. Fix the test or implementation
3. Retry (max 3 attempts)
4. If still failing after 3: **STOP** and report

### 2e. Quick Review

Check files changed in this task for critical issues:
- Type safety violations (any casts, missing types)
- Security issues (unsanitized input, hardcoded secrets)
- Missing error handling on async operations

**Auto-fix Blocker/High findings.** Skip Medium/Low/Info.

### 2f. Commit

```bash
git add <specific-files-changed>
git commit -m "<type>(<scope>): <description>

Task N from <plan-file>"
```

**Use Conventional Commits format.** Reference the plan task in the commit body.

### 2g. Report Progress

```
Task N/M: DONE — <brief summary>
  Files: <list of files created/modified>
  Commit: <sha>
```

If blocked:

```
Task N/M: BLOCKED — <failure description>
  Error: <build/test error message>
  Attempts: 3/3 exhausted
```

**STOP execution on BLOCKED.** Do NOT skip to the next task.

---

## Phase 3: Acceptance Gate

After ALL tasks complete:

### 3a. Full Code Review

Review the cumulative changeset:

```bash
git diff origin/main --name-only
```

Check for:
- TypeScript quality (types, unused code, error handling)
- Security (injection, secrets, auth)
- Test coverage (new code has tests?)
- API patterns (if applicable)

**Auto-fix Blocker/High findings** (max 3 cycles per finding):
1. Apply fix
2. Build and test
3. Commit: `fix: address <finding title>`
4. Re-review to confirm

### 3b. Plan Alignment Check

1. Re-read the original plan file
2. Compare against the cumulative diff
3. Verify:
   - **All tasks implemented?** Every task in the plan has a corresponding commit.
   - **No unplanned additions?** No extra files, features, or refactors beyond the plan.
   - **Spec match?** Implementation matches the plan's specification, not a reinterpretation.

Flag deviations as findings.

### 3c. Run Checkpoint

Run the full quality gate: lint + build + test.

### 3d. Calculate Verdict

| Verdict | Criteria |
|---------|----------|
| **PASS** | All tasks done, no Blocker/High remain, checkpoint passes, plan alignment clean |
| **WARN** | All tasks done, only Medium/Low remain, checkpoint passes |
| **FAIL** | Blocker/High remain, checkpoint fails, or plan alignment has gaps |
| **ABORT** | A Blocker is system-breaking and cannot be auto-fixed |

---

## Phase 4: Report

```
## Execution Report

**Plan:** <plan-file>
**Tasks:** N/N completed

### Per-Task Summary
| # | Description | Commit | Files | Status |
|---|-------------|--------|-------|--------|
| 1 | ... | abc1234 | 3 | DONE |
| 2 | ... | def5678 | 2 | DONE |

### Code Review Findings
- Blocker: N (N auto-fixed)
- High: N (N auto-fixed)
- Medium: N
- Low: N

### Plan Alignment
- All tasks implemented: YES/NO
- Unplanned changes: NONE / [list]
- Spec deviations: NONE / [list]

### Checkpoint
- Lint: PASS/FAIL
- Build: PASS/FAIL
- Tests: PASS/FAIL

### Verdict: PASS / WARN / FAIL / ABORT

[PASS]: Ready to ship. Create a PR.
[WARN]: Review Medium/Low findings before shipping.
[FAIL]: Fix listed issues before shipping.
[ABORT]: Critical issue — needs human review.
```

---

## Rules

1. **Follow the plan exactly.** Do NOT add unplanned features, refactors, or "improvements." The plan is the contract.
2. **Stop on persistent failure.** After 3 retries on build or test, STOP and report. Do NOT spiral into increasingly desperate fixes.
3. **Detect, don't assume.** Build commands, test commands, package names — detect all of these from the project. Never hardcode.
4. **Commits reference the plan.** Every commit message ties back to the task number and plan file.
5. **Report deviations.** If you must deviate from the plan (e.g., to fix a plan error), note exactly what changed and why.
