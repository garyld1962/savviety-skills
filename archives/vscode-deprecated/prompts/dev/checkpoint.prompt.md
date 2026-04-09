---
description: >-
  Run a quality gate: lint, build, and tests for changed packages.
  Does NOT run code review - use code-review for that.
agent: 'agent'
tools:
  - execute
  - read
  - search
---

# Checkpoint — Quality Gate

Fast quality gate that runs lint, build, and tests for changed packages. Does NOT run code review.

## When to Use

- Before pushing a branch
- Before creating a PR
- As a pre-merge validation
- After a batch of changes to verify nothing is broken

---

## CRITICAL: Do Not Guess

- **Package manager**: DETECT which manager is in use (pnpm, npm, yarn, bun). Check for lock files. Do NOT assume pnpm.
- **Script names**: Read `package.json` scripts. The lint command might be `lint`, `eslint`, `check`, or something else. Do NOT assume `pnpm -r lint`.
- **Test runner flags**: Check if the project uses vitest, jest, or another runner. Vitest needs `--run` to prevent watch mode. Jest does not. Do NOT add flags for the wrong runner.
- **Package names**: Use the `name` field from each package's `package.json`, NOT the directory name. They often differ.
- **Default branch**: Detect with `git symbolic-ref refs/remotes/origin/HEAD` or check for main vs master. Do NOT assume `main`.

---

## Step 1: Discover Tooling

### 1a. Detect package manager

```bash
ls pnpm-lock.yaml package-lock.json yarn.lock bun.lock 2>/dev/null
```

### 1b. Read project scripts

```bash
cat package.json | grep -E '"(lint|build|test|typecheck|check)"'
```

Also check `.github/copilot-instructions.md` for documented build/test commands.

### 1c. Record detected commands

```
Package manager: <detected>
Lint: <command or "not configured">
Build: <command>
Test: <command>
```

### Example: Correct detection

```
Package manager: pnpm (found pnpm-lock.yaml)
Lint: pnpm -r lint (from root package.json scripts.lint)
Build: pnpm -r build (from root package.json scripts.build)
Test: pnpm --filter <pkg> test -- --run (vitest detected, needs --run)
```

### Example: INCORRECT

```
# WRONG: Assuming commands without checking
Lint: eslint .  # ← Project might not have eslint directly, might use biome
Build: tsc      # ← Project might use a bundler, not bare tsc
```

---

## Step 2: Identify Changed Packages

### 2a. Detect default branch

```bash
DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
[ -z "$DEFAULT" ] && DEFAULT=$(git show-ref --verify --quiet refs/remotes/origin/master 2>/dev/null && echo master || echo main)
echo "Default branch: $DEFAULT"
```

### 2b. Get changed files

```bash
git diff origin/$DEFAULT --name-only
```

If no changes vs default branch, check uncommitted:

```bash
git diff --name-only
git diff --cached --name-only
```

### 2c. Map files to packages

For monorepos, map each changed file to its workspace package:

```bash
# Example: services/brain/src/index.ts → @bakerst/brain (or whatever the name is)
# Read the package.json in the containing directory
cat <package-dir>/package.json | grep '"name"'
```

Report: `"N files changed across M packages: [list]"`

If NO files are changed: **STOP** with "No changes detected. Nothing to check."

---

## Step 3: Run Linter

```bash
<detected-lint-command>
```

| Outcome | Action |
|---------|--------|
| Lint passes | Record PASS |
| Lint fails | Record output but CONTINUE to build |
| No lint configured | Record SKIP |

Do NOT try to run a linter that isn't configured.

---

## Step 4: Run Build / Typecheck

```bash
<detected-build-command>
```

| Outcome | Action |
|---------|--------|
| Build passes | Record PASS |
| Build fails | Record output but CONTINUE to tests |

---

## Step 5: Run Tests for Changed Packages

For EACH changed package:

```bash
<detected-test-command-for-package>
```

### Test runner specifics

| Runner | Watch mode prevention | Notes |
|--------|----------------------|-------|
| vitest | Add `--run` flag | Without it, vitest enters watch mode and never exits |
| jest | No flag needed | Exits after run by default |
| mocha | No flag needed | Exits after run by default |

**If a package has no test script:** Record SKIP for that package. Do NOT fail.

**Known pre-existing failures:** If project docs mention known failing tests, note them but do NOT let them block the verdict UNLESS they are new regressions (i.e., the same test was passing on the default branch).

---

## Step 6: Report

```
## Checkpoint Results

**Files changed:** N files across M packages
**Packages:** [list with actual package names]

| Check | Result | Details |
|-------|--------|---------|
| Lint | PASS/FAIL/SKIP | [summary or "not configured"] |
| Build | PASS/FAIL | [summary] |
| Tests | PASS/FAIL/SKIP | N passed, N failed [per package breakdown] |

**Verdict: PASS / FAIL**
```

### Verdict Logic

- **PASS**: All checks passed or were skipped (no failures).
- **FAIL**: Any check failed. List each failure with the relevant error output.

### Example: Full report

```
## Checkpoint Results

**Files changed:** 8 files across 2 packages
**Packages:** @bakerst/shared, @bakerst/brain

| Check | Result | Details |
|-------|--------|---------|
| Lint | PASS | No issues |
| Build | PASS | All packages compiled |
| Tests | PASS | 42 passed, 0 failed (shared: 18, brain: 24) |

**Verdict: PASS**
```

---

## Rules

1. **Detect everything.** Package manager, build commands, test commands, branch names — detect all from the project. Never assume.
2. **Continue on failure.** Lint failure doesn't skip build. Build failure doesn't skip tests. Run everything, report everything.
3. **No code review.** This is the FAST gate. Use the code-review prompt separately for thorough review.
4. **Known failures.** Document pre-existing test failures but don't let them block unless they're new regressions.
5. **Exact package names.** Use `name` from `package.json`, not directory names.
