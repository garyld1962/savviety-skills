---
description: >-
  Syncs the current branch with main via fetch and rebase, resolving merge
  conflicts with guidance. Focus on the conflict resolution workflow — Copilot
  already understands basic git state. Use when your branch is behind main and
  you need guided conflict resolution.
argument-hint: '[--base <branch>]'
agent: agent
tools:
  - execute
  - read
  - edit
---

# Sync Main

Bring the current feature branch up to date with main by fetching the latest
changes and rebasing your work on top. The primary value is conflict resolution
guidance — handle the rebase mechanics and walk the user through each conflict.

## Pre-flight

Check for uncommitted changes (`git status --porcelain`). If the tree is dirty,
stop and ask the user to commit or stash before proceeding.

If already on main, stop: "Already on main. Use `git pull` instead."

## Fetch and check divergence

Detect the default branch name from `git symbolic-ref refs/remotes/origin/HEAD`,
falling back to `master` then `main`. Fetch it, then report:

```
Branch:      <current>
Behind main: <N> commits
Ahead of main: <N> commits
```

If behind is 0: "Already up to date with main." Stop.

## Rebase

```bash
git rebase origin/<main>
```

If `--base <branch>` was passed, rebase on that branch instead.

## Conflict resolution

When `git rebase` stops with conflicts:

1. List conflicted files: `git diff --name-only --diff-filter=U`

2. For each conflicted file, apply the correct resolution rule:

   **Lock files** (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`,
   `Cargo.lock`, `go.sum`, etc.) — always take main's version (`git checkout
   --theirs <file>`), then regenerate the lock file using the project's install
   command (e.g. `npm install`, `cargo build`). Stage the regenerated file.
   Never hand-edit a lock file.

   **Generated files** (migration snapshots, compiled assets, OpenAPI outputs)
   — take main's version, then re-run the generation command. Ask the user for
   the generation command if it isn't obvious from the repo.

   **Code files** — show the conflict markers and ask the user which side is
   correct, or how to combine them. Never silently pick a side on code
   conflicts.

3. After all conflicts in a file are resolved, stage it: `git add <file>`

4. Continue: `git rebase --continue`

5. If a resolution attempt fails twice on the same file, stop trying. Run
   `git rebase --abort` to restore the original state, report what was
   attempted, and surface what's confusing.

## Abort is always safe

`git rebase --abort` restores the branch exactly as it was before the rebase
started. Offer this explicitly if the user wants to bail out.

## Post-rebase

After a successful rebase, warn the user if the branch has already been pushed:

> The branch history has changed. You will need `git push --force-with-lease`
> to update the remote. Do not force-push to a shared branch without
> coordinating with collaborators.

## Final report

```
Sync complete
  Branch:    <current>
  Commits from main applied: <N>
  Your commits replayed: <N>
  Status: clean
```

Suggest running `/checkpoint` to verify the build and tests still pass.
