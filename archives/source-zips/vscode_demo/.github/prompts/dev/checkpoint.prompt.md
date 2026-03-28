---
description: "Run a quality gate checkpoint: lint, build, and tests for changed packages. Does NOT run code review."
---

# Checkpoint — Quality Gate

Fast quality gate that runs lint, build, and tests for changed packages. Does NOT run code review.

## When to Use

- Before pushing a branch
- Before creating a PR
- As a pre-merge validation
- After a batch of changes to verify nothing is broken

## Workflow

### Step 1: Discover Tooling

Read `.github/copilot-instructions.md` and root `package.json` to identify:
- **Lint command**: e.g., `pnpm -r lint`
- **Build command**: e.g., `pnpm -r build`
- **Test command**: e.g., `pnpm --filter <pkg> test -- --run`
- **Package manager**: pnpm, npm, yarn, bun

### Step 2: Identify Changed Packages

```bash
git diff origin/main --name-only
```

Extract unique package/service paths. For pnpm monorepos, map file paths to workspace package names.

If no changes vs origin/main, check uncommitted changes:
```bash
git diff --name-only
git diff --cached --name-only
```

Report: "N files changed across M packages: [list]"

### Step 3: Run Linter (if configured)

```bash
pnpm -r lint
```

If no lint script exists, skip. If lint fails, record but continue.

### Step 4: Run Build / Typecheck

```bash
pnpm -r build
```

If build fails, record but continue to tests.

### Step 5: Run Tests for Changed Packages

For each changed package:
```bash
pnpm --filter <package-name> test -- --run
```

Use `--run` to prevent vitest watch mode.

### Step 6: Report

```
## Checkpoint Results

**Files changed:** N files across M packages
**Packages:** [list]

| Check      | Result | Details          |
|------------|--------|------------------|
| Lint       | PASS/FAIL/SKIP | [summary]  |
| Build      | PASS/FAIL | [summary]       |
| Tests      | PASS/FAIL/SKIP | [summary]  |

**Verdict: PASS / FAIL**
```

- **PASS**: All checks passed (or skipped with no failures).
- **FAIL**: Any check failed.

## Notes

- This is the fast gate. It does NOT run code review.
- Known pre-existing test failures (documented in `.github/copilot-instructions.md`) should be noted but not block unless new regressions.
