---
name: checkpoint
description: "Quality gate that discovers project tooling, runs linter, typecheck/build, and tests for changed packages. Use before pushing or creating PRs, after a batch of edits to verify lint/typecheck/tests still pass, or as a sanity gate inside larger flows. Do NOT use when you want review feedback instead of green tests (use the code-review skill), when no changes are staged or tooling is not yet configured, or when a full delivery flow is needed (use the execute-plan skill)."
---

# /checkpoint — Quality Gate

**Purpose:** Fast quality gate that runs lint, build, and tests for changed packages. Does NOT run code review — use `/code-review` separately for that.

## When to Use

- Before pushing a branch or creating a PR
- After a batch of edits to verify lint/typecheck/tests still pass
- As a sanity gate inside larger flows (invoked by `/pr`, `/ship`)

## When NOT to Use

- You want review feedback, not just green tests — use `/code-review`
- No changes staged or tooling not yet configured — run `/configure` first
- Full delivery flow needed — use `/pr` or `/ship`, which call checkpoint internally

Execute these steps in order. Report results at the end.

### Step 1: Read the repo-delivery contract

Read the repo's `CLAUDE.md` `## Commands` section for the required schema
(see `_rubrics/repo-delivery`). Required fields:

- `lint` — lint command
- `build` — build/typecheck command
- `test` — test command
- `package_manager` — pnpm, npm, yarn, bun, pip, poetry, cargo, go, dotnet, ...

If the `## Commands` section is missing, fail fast with:

```
Repo missing required CLAUDE.md ## Commands section.
See _rubrics/repo-delivery for the schema.
```

Do not infer commands from manifests. Do not fall back to `package.json`
scripts. The contract is declared; if it's absent, the repo is not ready
for this flow.

### Step 2: Identify Changed Packages

```bash
git diff origin/main --name-only
```

Extract unique package/service paths from the changed files. For a pnpm monorepo, map file paths to their workspace package names (check `pnpm-workspace.yaml` and each package's `package.json`).

If no changes vs origin/main, check for uncommitted changes:
```bash
git diff --name-only
git diff --cached --name-only
```

Report: "N files changed across M packages: [list]"

### Step 3: Run Linter (if configured)

```bash
pnpm -r lint
```

Or the project-specific lint command from Step 1.

- If no lint script exists, skip and note "No linter configured."
- If lint fails, record the output but continue to build.

### Step 4: Run Build / Typecheck

```bash
pnpm -r build
```

Or the project-specific build command from Step 1.

- If build fails, record the output but continue to tests.

### Step 5: Run Tests for Changed Packages

For each changed package identified in Step 2:

```bash
pnpm --filter <package-name> test -- --run
```

- Use `--run` to prevent vitest from entering watch mode.
- If a package has no test script, skip it and note "No tests for <package>."
- If tests fail, record the output.

### Step 6: Report

Output a summary:

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
- **FAIL**: Any check failed. List each failure with relevant output.

## Notes

- This is the fast gate. It does NOT run `/code-review`.
- `/pr` and `/ship` call this skill as a prerequisite.
- Known pre-existing test failures (documented in CLAUDE.md or auto-memory) should be noted but not block the verdict unless they are new regressions.
