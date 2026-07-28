# Session Context System

A lightweight convention for preserving work context across Claude Code sessions. Solves two recurring problems:

1. **Context loss between sessions.** When returning to a project after days or weeks, the agent reconstructs state from memory and git log, producing hallucinated assumptions. SESSION.md provides a durable, agent-readable record.
2. **Duplicate/conflicting PRs.** Agents occasionally open new PRs when one already exists on the same branch. The PR guardrail hook catches this before it happens.

## Components

### `/repo-status` — Session Start

Run this first in every new session when you need live repo state. It reads git state and open PRs, then prints a concise briefing:

```
📍 baker-street — feat/planner-v2
Last session: 2026-04-07T18:30:00Z on workstation-1

Where we left off:
Refactored the planner worker to use the new TaskQueue interface.
Three of five tests passing, two blocked on the mock setup.

Next action: Fix mock setup in test_planner_dispatch, then run full suite.

Git: clean, last commit a1b2c3d — refactor: extract TaskQueue interface
Open PRs (you): 1 — #42 "Planner worker refactor" (feat/planner-v2)
```

Warns on branch mismatch, machine mismatch, stashed work, and stale PRs.

### Journal Hooks — Session End

The `claude/infra/journal/` hooks capture session and commit context into `.claude/journal/`:

- **Where we left off** — what was done, what state it's in
- **Next action** — one specific concrete thing for the next session
- **Open questions** — unresolved decisions, unknowns
- **Don't forget** — gotchas, reminders, non-obvious context

`.claude/SESSION.md` and `.claude/journal/*.md` are **gitignored** per-machine working memory. History lives in git log and transcripts.

### PR Guardrail Hook

A `PreToolUse` hook on `gh pr create` that checks for existing open PRs before allowing the command. If any are found (especially on the current branch), it blocks and presents options:

1. Push to existing PR's branch instead
2. Stack a new branch on top
3. Close the existing PR first
4. Override and create anyway

Installed globally in `~/.claude/settings.json`. See `claude/infra/pr-guardrail/INSTALL.md`.

## Per-Repo Setup

Add this to each repo's `.gitignore`:

```
.claude/SESSION.md
```

Add this to each repo's `CLAUDE.md`:

```markdown
## Session context

This repo uses the session-context system.

- `.claude/SESSION.md` holds working memory from the previous session. Read it first.
- Run `/repo-status` at the start of every session when branch or PR state matters.
- Let the journal hooks capture session-end state when enabled.
- Never run `gh pr create` without first checking for existing open PRs — the
  PR guardrail hook will catch this, but prefer to check explicitly.
```

## Design Decisions

- **SESSION.md is gitignored.** Per-machine isolation — two machines may be mid-different-things on the same repo. No merge conflicts on scratchpad content.
- **PR guardrail is a Claude Code hook, not a GitHub branch rule.** Branch protection fires too late (after the agent has done work). The hook catches it at the intent layer so the agent can react intelligently.
- **Journal capture is hook-based.** The existing `/checkpoint` skill remains a quality gate (lint/build/test), not a session-memory command.

## Task Management Integration

This system is designed to integrate with the **Baker Street task management system** via its MCP server. The task management features (Linear session-state issues, cross-project dashboard, `savviety-status` command) described in the original design will be implemented through that integration rather than standalone skills.

## File Manifest

```
claude/
├── repo-status/SKILL.md                 # Live repo briefing skill
├── infra/journal/                       # Session journal hook scripts
├── infra/pr-guardrail/
│   ├── pr-guardrail.sh                  # Hook script (install globally)
│   └── INSTALL.md                       # Installation instructions
└── SESSION-CONTEXT.md                   # This file

Per-repo (created by the system):
  <repo>/.claude/SESSION.md              # Gitignored, per-machine working memory
```
