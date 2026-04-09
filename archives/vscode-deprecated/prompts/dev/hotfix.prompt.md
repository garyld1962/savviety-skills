---
description: "Apply an expedited fix for a critical production issue: branch from main, apply a scoped fix, run targeted tests, and fast-track merge."
argument-hint: "Describe the critical issue to fix..."
---

# Hotfix — Expedited Production Fix

Apply a targeted fix for a critical issue with minimal ceremony. Branches from main (or a release tag), fixes the specific problem, runs affected tests, and fast-tracks to merge.

## When to Use

- Production is broken and needs an immediate fix
- A critical bug was found right after a release
- The normal plan → execute-plan → code-review → ship pipeline is too slow

## When NOT to Use

- The bug is not critical — use `triage` → `plan` → `execute-plan` instead
- You don't understand the root cause yet — use `triage` first
- The fix requires significant refactoring — use the normal pipeline

## Arguments

- `<description>` — what's broken and how to fix it
- `--from <tag|sha>` — branch from a specific tag or commit (default: `main`)
- `--ado <item-id>` — link to an ADO work item for tracking

---

## Step 1: Create Hotfix Branch
```bash
git fetch origin
git checkout main && git pull origin main
git checkout -b hotfix/<short-description> main
```
If `--from <tag>`: branch from that tag instead.

## Step 2: Confirm Scope
Before writing any code, state:
- **What's broken:** one sentence
- **Root cause:** one sentence
- **Fix:** one sentence
- **Files to touch:** exact list

Ask user to confirm. The fix must be **minimal**.

## Step 3: Apply the Fix
- Touch only what's necessary. No refactors, no cleanup.
- Write a regression test for the specific bug.
- No new features.

## Step 4: Run Targeted Tests
```bash
pnpm --filter <affected-package> test -- --run
pnpm -r build
```
If tests/build fail: max 2 attempts, then stop.

## Step 5: Security Quick Check
Review for: no new secrets, no injection vulnerabilities, no auth bypasses, input validation intact.

## Step 6: Commit
```bash
git add <changed files>
git commit -m "hotfix(<scope>): <description>

Fixes: <root cause>
ADO: #<item-id> (if provided)"
```

## Step 7: Push & Create PR
```bash
git push -u origin HEAD
gh pr create --title "hotfix(<scope>): <description>" --body "..."
```

## Step 8: Merge
```bash
gh pr merge <pr-number> --squash --delete-branch
git checkout main && git pull origin main
```

## Step 9: Report
```markdown
## Hotfix Complete

**Branch:** hotfix/<name>
**PR:** #<number> — <title>
**Commit on main:** <sha>
**Tests:** PASS
**Fix:** <one-line summary>

### Next steps
- [ ] Verify fix in production
- [ ] File follow-up ADO item if deeper fix needed
- [ ] Update changelog
```

## Key Rules

- **Speed over ceremony.** Skip full plan and multi-specialist code review. Keep the security check.
- **Minimal scope.** The smallest correct change. Nothing more.
- **Always add a test.** The one thing you don't skip is the regression test.
- **Document for follow-up.** If the root cause needs a deeper fix, note it.
- **Don't use hotfix for non-critical issues.** The normal pipeline exists for a reason.
