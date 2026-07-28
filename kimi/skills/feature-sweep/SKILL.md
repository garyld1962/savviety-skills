---
name: feature-sweep
description: 'Audit installed skills against the latest Claude Code and API releases,
  then propose and optionally apply surgical integrations. Use when you want to capitalize
  on a new model release or Claude Code update — phrases like ''what new features
  can improve our skills'', ''sweep for new integrations'', ''update skills for the
  new model'', ''what Claude features are we not using''. When NOT to Use: improving
  skill quality or fixing bugs in a single skill (use /skill-improver); adding a new
  skill from scratch (use /new-skill).'
whenToUse: 'Audit installed skills against the latest Claude Code and API releases,
  then propose and optionally apply surgical integrations. Use when you want to capitalize
  on a new model release or Claude Code update — phrases like ''what new features
  can improve our skills'', ''sweep for new integrations'', ''update skills for the
  new model'', ''what Claude features are we not using''. When NOT to Use: improving
  skill quality or fixing bugs in a single skill (use /skill-improver); adding a new
  skill from scratch (use /new-skill).'
---


# /skill:feature-sweep — Integrate New Platform Features into Installed Skills

**Purpose:** Discover which installed skills would benefit from recently-released Claude Code or API capabilities, then propose (and optionally apply) minimal, surgical integrations. Treats skills as living artifacts — not set-and-forget after authoring.

## When to Use

- After a Claude model release (new Opus, Sonnet, extended thinking changes)
- After a Claude Code release (new slash commands, subagent architecture, /batch, scheduling)
- Periodically (quarterly) as a process-health check
- When you suspect skills were written before a feature existed that would now improve them

## When NOT to Use

- Fixing bugs or quality issues in a specific skill — use `/skill-improver`
- Writing a new skill from scratch — use `/new-skill`
- Auditing skill descriptions for trigger overlap — use `/validate-skills`

## Arguments

- `--apply` — after proposing integrations, apply approved changes immediately
- `--skill <name>` — scope to a single skill (otherwise sweeps all installed skills)
- `--feature <name>` — scope to a specific feature category (see Phase 2)
- `--since <date>` — only consider Claude features released after this date

## Phase 1: Discover Installed Skills

List all installed skills:

```bash
ls .claude/skills/
```

If `.claude/skills/` doesn't exist, check `~/.claude/skills/`. Build a list of skill names. If `--skill` was passed, filter to that one skill.

For each skill, read its `SKILL.md` frontmatter and first 20 lines to understand:
- What it does (description)
- What model it uses (if specified)
- What kind of work it performs (analysis, execution, interview, search, etc.)

Do not read the full content of every skill yet — that comes in Phase 3.

## Phase 2: Research New Features

Search for the latest Claude Code and Claude API releases. Look for:

1. **Extended / summarized thinking** — Claude's ability to reason privately before responding, with `effort` parameter replacing `budget_tokens`
2. **New slash commands** — `/batch`, `/loop`, `/schedule`, `/recap`, `/ultrareview`, or others
3. **Subagent architecture** — bounded permissions, independent context windows, persistent agent memory at `~/.claude/agent-memory/`
4. **Context window changes** — 1M token context availability on current models
5. **New MCP servers or tools** — built-in integrations now available
6. **Model lineup changes** — new Opus, Sonnet, Haiku versions and their capability differences
7. **Dreaming / background agents** — scheduled background review sessions

Summarize your findings as a feature list before proceeding. If `--feature` was passed, focus on that category. If `--since <date>` was passed, filter to features released after that date.

## Phase 3: Categorize Skills by Integration Opportunity

Map installed skills to feature opportunities using these heuristics. Don't read full skill files yet — use the short descriptions from Phase 1.

### Extended Thinking candidates
Skills that perform **analysis, judgment, synthesis, or comparison** where deeper reasoning would improve accuracy. Signals:
- Applies multiple lenses or perspectives and must reconcile them
- Filters false positives or calibrates severity
- Compares N options and recommends one
- Detects gaps or ambiguities in a document
- Makes a verdict that, if wrong, causes downstream harm

### `/batch` candidates
Skills that **decompose work and execute it at scale**, where independent parallelism per unit would reduce risk. Signals:
- Invokes `/skill:execute-prd`, `/skill:execute-plan`, or similar at the end
- Generates N tasks/moves/phases that are independent of each other
- Currently described as a "single large pass" that could be split
- Blast radius of failure is high (many files touched)

### Persistent memory candidates
Skills that **run repeatedly on the same project** and currently lose context between sessions. Signals:
- Used repeatedly across sessions (kickoff, daily workflow, process review)
- Makes architectural decisions that would be useful to remember
- Currently requires the user to re-explain project context

### 1M context candidates
Skills that **read code comprehensively** but currently sample or throttle reads due to context limits. Signals:
- Explicitly mentions "sample", "do not read every file", "stop at N% context"
- Produces investigation reports or holistic codebase assessments
- Currently limited by context, not by what's useful to read

### `/schedule` / Dreaming candidates
Skills that **run on a cadence** or accumulate signal over time. Signals:
- Described as "periodic" or "monthly/quarterly"
- Consumes artifacts produced by other skills over time
- Would benefit from automated, recurring execution

## Phase 4: Read Candidate Skills

For each skill identified as a candidate in Phase 3, read its full `SKILL.md`. You are looking for the specific step or section where the integration would land.

**For extended thinking:** find the step where judgment, synthesis, or comparison happens — immediately before that step is where the thinking instruction goes.

**For `/batch`:** find the Phase/Step that currently invokes `/skill:execute-prd` or `/skill:execute-plan` — that's where the `/batch` alternative goes.

**For persistent memory:** find the first step (where context should be loaded) and the last step after validation (where decisions should be saved).

**For 1M context:** find the reading strategy section — the token-budget or sampling rule that currently limits reads.

**For `/schedule`:** find the final report step — that's where the scheduling option and guidance goes.

## Phase 5: Propose Integrations

For each candidate, produce a concrete proposal in this format:

```
## [skill-name]

Feature: [extended thinking | /batch | persistent memory | 1M context | /schedule]

Where: [Step N: <step title>]

Change: [one sentence describing what gets added]

Before:
  [2-4 lines of the current text at that location]

After:
  [2-4 lines showing the proposed addition in context]

Impact: [what this improves — one sentence]
Risk: [any reason to be cautious — or "none"]
```

Produce the full proposal list before asking for approval. Do not apply any changes yet unless `--apply` was passed.

**Proposal rules:**
- Each change must be **additive only** — no rewrites of existing behavior
- Extended thinking instructions must be positioned **before** the step that uses them, not inside it
- Memory reads must be positioned at the **start** of the skill's workflow; writes at the **end**
- `/batch` must be a **flag or conditional** — never replace the existing execution path entirely
- Scheduling must be **optional** — never auto-register without explicit user action

## Phase 6: Apply (if approved)

If `--apply` was passed, or after the user reviews and approves specific proposals:

For each approved change:
1. Read the full current skill file
2. Apply the change using targeted string replacement
3. Confirm the edit landed correctly
4. Report: "Applied [feature] to [skill-name] at [step]"

Do not batch multiple changes into a single edit. Apply one skill at a time.

After all changes are applied:

```
Feature sweep complete.

Applied: <N> integrations across <M> skills

Extended thinking:  <list of skills>
/batch:             <list of skills>
Persistent memory:  <list of skills>
1M context:         <list of skills>
/schedule:          <list of skills>

Skipped (no opportunity found): <list of skills>
Deferred (needs follow-up):     <list of skills>
```

## CRITICAL: Surgical Changes Only

- Do NOT rewrite existing skill logic. The integration touches one step; everything else stays verbatim.
- Do NOT change the model used by a skill unless extended thinking requires Opus and the skill is on a weaker model. State this explicitly and ask before changing.
- Do NOT add features beyond what a specific Claude capability enables. No speculative improvements.
- Do NOT propose an integration for a feature that isn't confirmed as released. If you're uncertain whether a feature exists, say so.
- Do NOT apply changes the user hasn't approved. Proposals first, changes second.

## Contract

- **Inputs:** installed skills in `.claude/skills/` (or `~/.claude/skills/`). Optional: `--apply`, `--skill <name>`, `--feature <name>`, `--since <date>`.
- **Preconditions:** operator is at the keyboard — proposals require human review before changes are applied.
- **Outputs:** a proposal document listing per-skill integrations with before/after diffs. When `--apply` is confirmed: edited skill files and a summary of changes made.
- **Postconditions:** each modified skill gains one targeted integration; no existing behavior is removed or restructured.
- **Failure modes:** no new features found relevant to installed skills → report "no integrations identified, sweep complete"; a skill has no identifiable integration point → mark as "deferred, no clear insertion point found" and skip.
