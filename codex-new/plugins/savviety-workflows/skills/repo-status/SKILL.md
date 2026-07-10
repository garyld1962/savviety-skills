---
name: repo-status
description: "Read-only live repo snapshot: branch, upstream, working tree, stashes, recent commits, unpushed commits, and current user's open GitHub PRs. Use at session start, before delivery, or when repo state is unclear."
---

# Repo Status

Print a concise read-only snapshot of the current repository.

## Workflow

1. Run `python3 <skill-root>/scripts/repo_status.py` from the target repo.
2. Add `--full` when the user asks for more detail.
3. Do not run mutating commands: no fetch, pull, push, checkout, stash apply, or PR creation.
4. If `gh` is missing or unauthenticated, report the git state and say PR lookup was skipped.

## Output Rules

- Keep default output to one screen.
- Report facts, not remembered assumptions.
- Surface warnings for no upstream, behind upstream, unpushed commits, stashes, detached HEAD, and stale current-branch PRs.
