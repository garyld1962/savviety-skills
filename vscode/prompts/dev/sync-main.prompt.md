---
description: >-
  Sync current branch with main: fetch latest, rebase or merge, resolve
  conflicts. Use when your branch is behind main or before creating a PR.
argument-hint: '[--stash] [--merge]'
agent: 'agent'
tools:
  - execute
  - read
  - search
---

# Sync Branch with Main

Bring the current feature branch up to date with the main branch. Fetches latest changes, rebases your work on top, and handles conflicts.

## When to Use

- Before creating a PR (ensure no merge conflicts)
- When main has moved ahead and you need the latest changes
- After another PR was merged and you need its changes

## When NOT to Use

- You are already on main — just run `git pull`
- You have uncommitted changes and did not pass `--stash`

## Arguments

- `--stash` — automatically stash and pop uncommitted changes around the sync
- `--merge` — use merge instead of rebase (safer for branches with multiple contributors)

---

## CRITICAL: Do Not Guess

- **Branch names**: Run `git branch --show-current` to get the current branch. Do NOT assume it is called "feature" or "dev."
- **Default branch**: Detect the default branch name. Do NOT assume it is `main` — it could be `master`, `develop`, or something else. Use the detection commands in Step 2.
- **Conflict resolution**: NEVER silently pick a side on code conflicts. Lock files (pnpm-lock.yaml, package-lock.json, yarn.lock) can be auto-resolved. Code conflicts MUST be shown to the user.
- **Remote name**: Do NOT assume the remote is called `origin`. Verify with `git remote`.

---

## Step 1: Pre-flight Checks

### 1a. Get current branch

```bash
git branch --show-current
```

**STOP** if the output is `main` or `master` — tell the user: "Already on the default branch. Use `git pull` instead."

### 1b. Check for uncommitted changes

```bash
git status --porcelain
```

**If output is non-empty AND `--stash` was passed:**

```bash
git stash push -m "sync-main auto-stash"
```

**If output is non-empty AND `--stash` was NOT passed:**

**STOP** — tell the user: "Uncommitted changes detected. Commit them, stash manually, or re-run with `--stash`."

### Example: Pre-flight output

```
Branch: feat/user-auth
Status: clean
Proceeding with sync...
```

---

## Step 2: Detect Default Branch and Fetch

### 2a. Detect the default branch name

Run these commands IN ORDER. Use the first one that succeeds:

```bash
# Method 1: symbolic ref (most reliable)
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'

# Method 2: check for master vs main
git show-ref --verify --quiet refs/remotes/origin/master && echo master || echo main
```

**Do NOT skip detection and assume `main`.** The wrong branch name will cause the rebase/merge to fail or target the wrong base.

### 2b. Fetch latest

```bash
git fetch origin <detected-branch>
```

### Example: Correct detection

```
Detected default branch: main
Fetching origin/main...
```

### Example: INCORRECT (do not do this)

```
# WRONG: Hardcoding "main" without checking
git fetch origin main  # ← What if it's "master" or "develop"?
```

---

## Step 3: Check Divergence

```bash
BEHIND=$(git rev-list --count HEAD..origin/<default-branch>)
AHEAD=$(git rev-list --count origin/<default-branch>..HEAD)
```

**Report to user:**

```
Branch: <current>
Behind <default-branch>: <N> commits
Ahead of <default-branch>: <N> commits
```

**If behind is 0:** Tell the user "Already up to date with <default-branch>." Pop stash if applicable and **STOP**.

---

## Step 4: Sync

### 4a. Rebase (default — when `--merge` was NOT passed)

```bash
git rebase origin/<default-branch>
```

### 4b. Merge (when `--merge` was passed)

```bash
git merge origin/<default-branch> --no-edit
```

### Handling Conflicts

If either command produces conflicts:

1. **List conflicted files:**

   ```bash
   git diff --name-only --diff-filter=U
   ```

2. **For lock files** (pnpm-lock.yaml, package-lock.json, yarn.lock, Cargo.lock): Auto-resolve by accepting theirs:

   ```bash
   git checkout --theirs <lock-file>
   git add <lock-file>
   ```

3. **For code files**: Show the conflict markers to the user and **ASK how to resolve.** Do NOT pick a side.

   ```
   CONFLICT in src/auth.ts (lines 42-58):
   <<<<<<< HEAD
   [your changes]
   =======
   [their changes]
   >>>>>>> origin/main

   How would you like to resolve this?
   a) Keep your changes
   b) Keep their changes
   c) Let me edit manually
   ```

4. **After all conflicts resolved:**

   ```bash
   # For rebase:
   git rebase --continue

   # For merge:
   git add . && git commit --no-edit
   ```

5. **If resolution fails after 2 attempts:** Abort and report:

   ```bash
   git rebase --abort   # or: git merge --abort
   ```

   Tell the user: "Sync aborted after 2 failed resolution attempts. No changes were made."

---

## Step 5: Post-Sync

### 5a. Pop stash (if `--stash` was used)

```bash
git stash pop
```

If stash pop has conflicts, report them but do NOT abort — the sync itself succeeded.

### 5b. Warn about force-push

If rebase was used (not merge), check if the branch has been pushed:

```bash
git log --oneline origin/<current-branch>..HEAD 2>/dev/null
```

If the branch exists on the remote, warn the user:

```
⚠ Your branch history has changed due to rebase. You will need
  to force-push: git push --force-with-lease origin <branch>

  Do NOT use --force (unsafe). Use --force-with-lease (safe).
```

**Do NOT force-push automatically.** Always let the user decide.

---

## Step 6: Report

```
Sync Complete
  Branch:    <current>
  Strategy:  rebase / merge
  Commits:   <N> from <default-branch> applied
  Your work: <N> commits replayed on top
  Status:    clean / stash conflicts (manual resolution needed)

Next: run a build/test check to verify everything still works.
```

---

## Rules

1. **Never force-push without explicit user approval.** Warn and let them decide.
2. **Lock files get auto-resolved.** Accept the default branch version, then let the user regenerate.
3. **Code conflicts require human input.** NEVER silently pick a side.
4. **Abort is safe.** If anything goes wrong, `git rebase --abort` or `git merge --abort` restores the previous state.
5. **Always report divergence.** The user should know how far behind they are before deciding to sync.
