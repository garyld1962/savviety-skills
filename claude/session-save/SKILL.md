---
name: session-save
description: "Session-end state capture: writes SESSION.md with current work context so the next session can resume without context loss. Run before ending a session."
---

# /session-save — Save Session Context

**Purpose:** Capture the current work context into `.claude/SESSION.md` so the next session (potentially on a different machine, days later, with a fresh agent) can resume without reconstructing state from memory and git log.

This is the counterpart to `/whereami`. Where `/whereami` reads, `/session-save` writes.

## Arguments

- _(none)_ — generate and write SESSION.md from current conversation context
- `--dry-run` — show what would be written without saving

## Workflow

### 1. Gather context

Read the current state from the environment:
- `git branch --show-current` — current branch
- `git log -1 --format='%h — %s'` — last commit
- `hostname` — current machine
- Current ISO timestamp

### 2. Generate session state

From the conversation context, generate:

- **Where we left off** (2-4 sentences): What work was done this session? What's the current state of that work? Is it complete, partial, blocked?
- **Next action** (one specific, concrete thing): What should the next session do first? Not vague ("continue working") — specific ("run the test suite for the auth module, then fix the failing `test_token_refresh` case").
- **Open questions** (bullet list): Things that came up but weren't resolved. Decisions deferred. Unknowns that need investigation.
- **Don't forget** (bullet list): Gotchas, notes, reminders. Things that aren't obvious from the code. "The staging DB has a schema mismatch — run migration before testing." "PR #42 is waiting on @alice's review."

### 3. Write SESSION.md

Write to `.claude/SESSION.md` using this format:

```markdown
# Session State: <repo basename>

**Last updated:** <ISO timestamp>
**Machine:** <hostname>
**Branch:** <current branch>
**Last commit:** <short sha> — <subject>

## Where we left off

<2-4 sentence prose summary of current work in progress>

## Next action

<one specific concrete thing to do when you come back>

## Open questions

- <question 1>
- <question 2>

## Don't forget

- <reminder 1>
- <reminder 2>
```

### 4. Ensure gitignore

Check if `.claude/SESSION.md` is gitignored. If not, warn:

"⚠️  `.claude/SESSION.md` is not in .gitignore. This file is per-machine working memory and should not be committed. Add `.claude/SESSION.md` to your .gitignore."

Do NOT modify .gitignore automatically — just warn.

### 5. Confirm

Print:
```
Session state saved to .claude/SESSION.md
Branch: <branch> | Commit: <sha> | Machine: <hostname>
Next session: run /whereami to restore context.
```

## Rules

- **Be specific, not vague.** "Continue the auth refactor" is useless. "Wire the new `TokenService` into `AuthMiddleware`, then run `npm test -- --grep auth`" is useful.
- **Capture what's NOT in the code.** The code and git log are already durable. SESSION.md's value is the prose context that lives only in the conversation: why a decision was made, what was tried and didn't work, what the user said they wanted.
- **Overwrite, don't append.** Each save replaces the previous SESSION.md entirely. History lives in git log and conversation transcripts — SESSION.md is current state only.
- **Don't lie.** If the session was trivial (just reading files, answering questions), say so. An honest "no meaningful work done" is better than fabricated state.
- **Include warnings.** If there's uncommitted work, note it. If there's a half-finished change, note it. The next session needs to know what's messy.
