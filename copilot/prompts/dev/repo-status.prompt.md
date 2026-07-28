---
description: >-
  Prints a concise snapshot of live repo state — branch, working tree, unpushed
  commits, stashes, and open PRs. Read-only. Use to orient at session start or
  after a break. For deeper PR inspection use /pr built-in; for diff inspection
  use /diff built-in.
---

# /repo-status — Live Repo Snapshot

> **Built-in first:** Use `/diff` for changed scope inspection and `/pr` for PR state. Use this prompt when you want a single combined repo orientation snapshot.

**Purpose:** Print a concise, current view of the repo's git and PR state. No memory, no narrative — just the facts needed to decide what to do next.

## When to Use

- Start of a session, to confirm the working tree is in the expected state.
- After switching machines or resuming work after a break.
- Before opening a PR, to confirm the branch is pushed and clean.
- Any time the current branch, push state, or PR status is unclear.

## When NOT to Use

- To inspect changed file contents — use `/diff` instead.
- To investigate a specific PR in detail — use `/pr` instead.
- To make any changes. This prompt is strictly read-only.

## Arguments

- _(none)_ — current repo, summary form
- `--full` — include 10-commit log, full PR details, and remote tracking detail

## Workflow

### 1. Repo Identity

- `git rev-parse --show-toplevel` — repo root
- Repo name from the basename of that path
- `hostname` — current machine

### 2. Branch and Tracking

- `git branch --show-current` — current branch
- `git rev-parse --abbrev-ref --symbolic-full-name @{u}` — upstream (note if branch has no upstream)
- `git rev-list --left-right --count @{u}...HEAD` — ahead/behind counts (skip if no upstream)

### 3. Working Tree

- `git status --short` — modified/untracked summary
- `git stash list` — stashes (count and first line of each)

### 4. Commits

- `git log --oneline -5` (or `-10` with `--full`) — recent commits on current branch
- If ahead of upstream: `git log --oneline @{u}..HEAD` — list unpushed commits explicitly

### 5. Open PRs

- `gh pr list --author @me --state open --json number,title,headRefName,updatedAt,isDraft,statusCheckRollup`
- Identify whether the current branch has an open PR
- Flag PRs older than 3 days as stale
- With `--full`: include CI status rollup per PR

### 6. Print Briefing

Default form:

```
<repo> — <branch> @ <machine>
Tracking: <upstream> (<ahead> ahead, <behind> behind)   [or: no upstream]
Working tree: <clean | N modified, M untracked>
Stashes: <count>   [omit if zero]

Unpushed commits:
  <sha> <subject>
  ...
[omit section if ahead == 0]

Recent commits:
  <sha> <subject>
  ...

Open PRs (you): <count>
  #<num> <title> — <branch> [draft] [CI: pass/fail/pending] (updated <relative>)
  ...
[omit section if zero]
```

### 7. Warnings

Append at the bottom only when triggered:

- Branch has no upstream — push with `-u` before opening a PR.
- Behind upstream by N — pull or rebase before continuing.
- Unpushed commits on current branch — N commits not on remote.
- Stashed work exists — N stashes, oldest from <date>.
- Open PR on current branch is stale — last update <relative>.
- Detached HEAD — not on any branch.

## Rules

- **Read-only.** Never run anything that mutates state (no `fetch`, no `pull`, no `push`, no stash apply). The user decides what to do next.
- **One screen.** Default output fits on a single screen. Use `--full` for detail.
- **Facts only.** Do not interpret history or make recommendations beyond the warnings listed above.
- **Fail gracefully.** If `gh` is missing or unauthenticated, print the git portion and note "PR check skipped: gh unavailable." Do not abort the briefing.
- **No network calls beyond `gh pr list`.** Do not `git fetch` — the user may be offline or on a slow connection.
