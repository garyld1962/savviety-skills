---
name: whereami
description: "Session-start briefing: reads SESSION.md, git state, and open PRs to restore context. Run this first in every new session."
---

# /whereami — Session Context Briefing

**Purpose:** Restore context at the start of a new session. Reads the local session state file, git status, and open PRs, then prints a concise briefing so neither the agent nor the user starts from a blank slate.

**This is the single command to learn.** Everything else — reading SESSION.md, checking git, checking PRs — happens behind it.

## When to Use

- Start of every new session — before any other work
- After returning from a long break to a project
- When the agent feels disoriented about branch, PR, or in-flight state

## When NOT to Use

- Ending a session — use `/session-save` instead
- You already have full context from the current conversation

## Arguments

- _(none)_ — brief the current repo
- `--full` — include recent git log (10 commits) and full PR details

## Workflow

### 1. Read session state

Check if `.claude/SESSION.md` exists in the current repo.

**If it exists:** read it and extract:
- Last updated timestamp
- Machine name
- Branch at time of save
- "Where we left off" prose
- "Next action"
- "Open questions"
- "Don't forget" items

**If it does not exist:** note "No session state found — this is either a new project or the first session. Consider running `/session-save` before ending this session."

### 2. Read git state

Run these commands and capture output:
- `git branch --show-current` — current branch
- `git status --short` — working tree state (clean or N files changed)
- `git log --oneline -5` — recent commits (or -10 with `--full`)
- `git stash list` — any stashed work

If the session state exists, compare:
- Is the current branch the same as the saved branch? If different, note it: "⚠️  Branch changed since last session: was `feat/foo`, now on `main`"
- Is the last commit different? If so, note commits since the saved one.

### 3. Check open PRs

Run: `gh pr list --author @me --state open --json number,title,headRefName,updatedAt`

If the current branch has an open PR, highlight it. List all open PRs by this user on this repo.

### 4. Check machine context

Get the current hostname: `hostname`

If SESSION.md records a different machine than the current one, warn:
"⚠️  Last session was on **{saved_machine}**, you're on **{current_machine}** — verify branch is pushed and working tree is clean."

### 5. Print briefing

Format:

```
📍 <repo name> — <current branch>
Last session: <timestamp> on <machine>

Where we left off:
<prose from SESSION.md>

Next action: <from SESSION.md>

Open questions:
- <question 1>
- <question 2>

Don't forget:
- <reminder 1>

Git: <clean|N files changed>, last commit <sha> <subject>
Open PRs (you): <count> — #<num> <title> (<branch>), ...
```

If no SESSION.md exists, skip the "Where we left off" / "Next action" / "Open questions" / "Don't forget" sections and just show git + PR state.

### 6. Warnings (if any)

Append any warnings at the bottom:
- ⚠️  Branch mismatch (current vs saved)
- ⚠️  Machine mismatch (current vs saved)
- ⚠️  Stashed work exists
- ⚠️  Open PRs older than 3 days

## Rules

- **Read, don't guess.** Every piece of the briefing comes from a file or command. Do not fill in gaps from conversation memory or assumptions.
- **Be concise.** The briefing should fit on one screen. Don't dump raw git log — summarize.
- **Don't start work.** This skill is read-only. It restores context so the user can decide what to do next.
- **Always run this first** in a new session, before doing any work. If SESSION.md exists, its contents are more reliable than anything in the agent's memory.
