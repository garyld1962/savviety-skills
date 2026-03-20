---
description: >-
  Plan a dependency migration: analyze breaking changes, assess codebase impact,
  produce a step-by-step migration plan. Use when upgrading Node, TypeScript,
  frameworks, or major dependencies.
argument-hint: '<package> <from-version> <to-version> [--scope <path>] [--dry-run]'
agent: 'agent'
tools:
  - execute
  - read
  - search
  - web
  - codebase
---

# Dependency Migration Planner

Analyze breaking changes for a dependency upgrade and produce a codebase-specific migration plan. Reads the changelog, maps breaking changes to your code, estimates scope, and generates an ordered task list.

## When to Use

- Upgrading Node.js (e.g., 20 → 22)
- Upgrading TypeScript (e.g., 5.3 → 5.7)
- Upgrading a framework (React 18 → 19, Next.js 14 → 15, Express 4 → 5)
- Upgrading a major dependency (Vitest 1 → 2, ESLint 8 → 9)
- When a dependency audit flags a major version update

## When NOT to Use

- Patch or minor updates — just update and run tests
- Adding a new dependency — not a migration
- Removing a dependency — just delete it

## Arguments

- `<package>` — the package or runtime to migrate (REQUIRED)
- `<from-version>` — current version (REQUIRED)
- `<to-version>` — target version (REQUIRED)
- `--scope <path>` — limit analysis to a specific package/directory
- `--dry-run` — analyze only, do not write a plan file

---

## CRITICAL: Do Not Guess

- **Breaking changes**: ALWAYS read the official migration guide, changelog, or release notes. Do NOT list breaking changes from memory — your training data may be outdated or wrong. Use web search to find the actual documentation.
- **Current version**: Verify the ACTUAL installed version. Do NOT trust what the user says without checking:
  ```bash
  cat package.json | grep '"<package>"'
  # or
  npx <package> --version
  ```
- **Codebase impact**: Search for ACTUAL usage in the codebase before claiming a breaking change affects the project. A breaking change that does not match any code in the project is NOT a task.
- **Compatibility**: Check ACTUAL dependency compatibility, not assumed. A plugin that worked with v8 may or may not work with v9 — verify by checking the plugin's package.json `peerDependencies` or its changelog.
- **File paths**: Search and verify. Do NOT invent paths like "probably in src/config/" without checking.

---

## Step 1: Gather Breaking Changes

### 1a. Fetch Official Migration Guide

Search for the official migration guide or changelog using web search:

1. Search: `"<package> migrate from <from> to <to>" site:github.com OR site:<package-docs-domain>`
2. Check the package repository for `CHANGELOG.md`, `MIGRATION.md`, or `UPGRADING.md`
3. Check GitHub releases between the two versions

**If no official migration guide is found:** State this clearly. Do NOT fabricate breaking changes. Report: "No official migration guide found. Proceeding with changelog analysis and ACTUAL version comparison."

### 1b. Classify Each Breaking Change

For every breaking change you find in the OFFICIAL documentation, classify it:

| Type | Impact | Example |
|------|--------|---------|
| **API Removal** | Must fix — code won't compile/run | `fs.exists()` removed |
| **API Rename** | Must fix — find-and-replace | `render()` → `createRoot().render()` |
| **Behavior Change** | May fix — tests will catch | Default encoding changed |
| **Type Change** | Must fix (TypeScript) | Return type widened/narrowed |
| **Config Change** | Must fix — build/runtime config | New config format required |
| **Default Change** | May fix — behavior differs silently | `strict: true` now default |
| **Deprecation** | Should fix — works now, breaks later | Warning on old API usage |
| **New Requirement** | Must fix — prerequisites | Requires Node >= 18 |

### Example: Correct breaking change entry

```
Source: https://eslint.org/docs/latest/use/migrate-to-9.0.0

1. API Removal: eslintrc config format removed
   - Must migrate to flat config (eslint.config.js)
   - All .eslintrc.* files must be converted
```

### Example: INCORRECT

```
# WRONG: Listing breaking changes from memory without verification
1. "I believe they changed the default parser"  # ← Don't believe, VERIFY
```

---

## Step 2: Scan Codebase for Impact

For EACH breaking change from Step 1, search the codebase:

```bash
# Search for removed/renamed API usage
grep -r "oldApiName" --include='*.ts' --include='*.tsx' --include='*.js' --include='*.jsx' src/

# Search for config files that need updating
find . -name "tsconfig.json" -o -name ".eslintrc.*" -o -name "vite.config.*"
```

For each match, record:
1. **File path and line number** (exact — verified by search)
2. **Source or test code?** (tests may need different treatment)
3. **Direct usage or behind an abstraction?** (if behind a wrapper, only the wrapper needs changing)

### Build Impact Matrix

```
| Breaking Change | Files Affected | Severity | Auto-fixable? |
|-----------------|----------------|----------|---------------|
| Removed X API | 5 files | High | Yes (rename) |
| New config format | 1 file | Medium | Yes (codemod) |
| Behavior change Y | 12 files | Low | No (manual review) |
| Changed default Z | 0 files | None | N/A — skip |
```

**If a breaking change has 0 files affected:** Do NOT include it as a task. Report it as "documented but does not affect this codebase."

---

## Step 3: Check Dependency Compatibility

For major framework upgrades, check that plugins and companion libraries are compatible:

```bash
# Check current dependencies
cat package.json | grep -E '"(eslint-plugin|@typescript-eslint|vite-plugin|babel-plugin)"'

# For each plugin, check if it supports the target version
# Check peerDependencies in node_modules/<plugin>/package.json
cat node_modules/<plugin>/package.json | grep -A 5 '"peerDependencies"'
```

**Common compatibility issues:**
- ESLint plugins with new ESLint major versions
- Babel plugins with new TypeScript versions
- Testing libraries with new framework versions
- Build tool plugins with framework upgrades

Flag any dependency that:
- Does NOT have a release compatible with the target version (check `peerDependencies`)
- Has known issues (check its GitHub issues page)

### Example: Compatibility finding

```
INCOMPATIBLE: eslint-plugin-import@2.29.0
  peerDependencies: { "eslint": "^8.0.0" }
  Target: ESLint 9
  Action: Need eslint-plugin-import@2.30+ or find alternative
```

---

## Step 4: Estimate Scope

| Files Affected | Scope | Approach |
|----------------|-------|----------|
| 0-5 | Small | Inline changes, no plan file needed |
| 6-20 | Medium | Plan file, single pass |
| 21+ | Large | Plan file, phased approach |

For large migrations, suggest phases:
1. Update build config and fix compilation errors
2. Update API usage (auto-fixable changes)
3. Manual behavior change review
4. Update tests for new behavior
5. Remove deprecated usage

---

## Step 5: Write Migration Plan

Unless `--dry-run` was passed, write to `docs/plans/YYYY-MM-DD-migrate-<package>-<from>-to-<to>.md`:

```markdown
# Migration: <package> <from> → <to>

## Summary
- **Package:** <name>
- **From:** <from-version>
- **To:** <to-version>
- **Scope:** <N> files affected across <M> packages
- **Estimated effort:** small / medium / large
- **Source:** <URL to official migration guide>

## Prerequisites
- [ ] Verify all tests pass on current version
- [ ] Check dependency compatibility (see below)
- [ ] Create a migration branch

## Dependency Compatibility
| Dependency | Current | Compatible with <to>? | Action |
|------------|---------|----------------------|--------|
| <dep> | <ver> | Yes/No/Unknown | Update to <ver> / Wait / Replace |

## Breaking Changes & Tasks

### Task 1: <breaking change title>
**Type:** API Removal / Rename / Behavior Change / etc.
**Severity:** High / Medium / Low
**Files:** <exact file list from codebase search>
**Change:** <what to change, with before/after examples>
**Auto-fixable:** Yes (codemod) / No (manual)

[Repeat for each breaking change that ACTUALLY affects the codebase]

## Migration Order
1. Update package version in package.json
2. [ordered tasks based on dependency chain]
3. Run build — fix compilation errors
4. Run tests — fix behavior changes
5. Remove deprecated usage

## Rollback Plan
1. `git checkout <pre-migration-branch>`
2. Revert version in lock file
3. Run install command to regenerate lock file

## Verification
- [ ] Build passes
- [ ] All tests pass
- [ ] No deprecation warnings in logs
- [ ] Smoke test key functionality
```

---

## Step 6: Report

```
Migration Analysis: <package> <from> → <to>

  Source: <URL to migration guide>
  Breaking changes: <N> documented, <M> affect this codebase
  Files affected: <N> across <M> packages
  Auto-fixable: <N> of <M> changes
  Dependency conflicts: <N>

  Scope: small / medium / large
  Plan: <path to plan file> (or "dry-run — no file written")

  Top risks:
  1. <highest risk change — why it's risky>
  2. <next risk>

  Next: Review the plan, then execute the migration tasks.
```

---

## Rules

1. **Research first.** ALWAYS read the official migration guide before scanning code. Do NOT rely on your training data for breaking changes — documentation is the source of truth.
2. **Don't migrate blindly.** Every change must be mapped to actual code in the codebase. A breaking change that doesn't affect your code is not a task.
3. **Test before and after.** The migration plan always starts with "verify tests pass" and ends with "run full test suite."
4. **Rollback is mandatory.** Every migration plan must include a rollback strategy.
5. **Phased is better than big-bang.** For large migrations, suggest incremental phases that can each be tested independently.
6. **Check the ecosystem.** A dependency upgrade often cascades — plugins, extensions, and complementary libraries may also need updates.
7. **Cite your sources.** Every breaking change must include a URL or document reference. If you cannot find a source, say so explicitly.
