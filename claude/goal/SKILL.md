---
name: goal
description: "Clarify and validate a development goal before writing a PRD. Use when the user has an idea or intent but hasn't shaped it into requirements yet — phrases like 'I want to build X', 'I'm thinking about adding Y', 'we should improve Z', 'what should we work on next', 'help me think through this idea'. Separates outcomes from solutions before any implementation work begins. When NOT to Use: requirements already written (use /prd-validate); specific bug to fix (use /triage); design decision to explore (use /design-twice)."
model: opus
---

# /goal — Goal Capture and Validation

**Purpose:** Turn a vague intent into a validated outcome statement before requirements are written. The most common failure mode in software is building the right feature for the wrong goal — this skill catches that before any PRD exists.

The key question this skill answers: **is this describing an outcome (what changes for users?) or a solution (what gets built?)**

## When to Use

- An idea or intent exists but no requirements artifact does
- The user says "I want to build X" or "we should improve Z"
- The motivation behind a proposed feature needs clarifying
- You want to validate that a proposed effort solves a real problem

## When NOT to Use

- Requirements are already written → `/prd-validate`
- A specific bug is known → `/triage`
- Exploring API/interface shape → `/design-twice`
- A goal is already clear and you're ready to write the PRD, ontology, and AERS → `/prd-create`

## Arguments

- `<description>` — plain-language description of what the user wants to achieve (optional; if omitted, ask)
- `--linear` — create a Linear issue to persist the validated goal
- `--append <file>` — append the goal statement to a file (default: `goals.md` in the repo root)
- `--no-persist` — produce the goal statement only, no file or issue written

## Workflow

### Step 1: Capture

If `<description>` was provided, use it. Otherwise ask:

> "What do you want to achieve? Describe it in plain language — no structure needed."

Accept whatever comes. Don't ask for a format.

### Step 2: Stress-Test (Extended Thinking)

**Before asking any clarifying questions**, engage extended thinking to reason through:

1. **Outcome vs. solution?** Is the description stating what changes for users/the system, or what gets built? Examples:
   - Solution-shaped: "add a dashboard", "refactor the auth module", "build an API endpoint"
   - Outcome-shaped: "operators need visibility into job status", "auth reliability is blocking customer onboarding", "partners need programmatic access to X"

2. **Real problem?** What is the underlying need driving this? Is the stated goal the root cause or a symptom?

3. **Success criteria?** What would have to be true for this goal to be considered achieved? Is that measurable?

4. **Scope boundary?** What is explicitly out of scope? What adjacent problems should NOT be pulled in?

5. **Assumptions?** What is being assumed to be true about users, the system, or the business? Which assumptions are load-bearing?

Use this reasoning to identify the 2-3 questions that will most sharpen the goal. Do not surface every question — only the ones that would materially change the goal statement.

### Step 3: Clarify

Ask at most 3 questions, one at a time. Prefer multiple-choice with a recommended default. Ground each question in what the stress-test surfaced.

Examples of the kinds of gaps to probe:
- "Is this goal about [outcome A] or [outcome B]? I'd default to [A] because [reason]."
- "Who is the primary beneficiary — [user type A] or [user type B]?"
- "What does success look like in 30 days? Specifically: what is different that isn't different now?"

If the description is already outcome-shaped with clear success criteria, skip to Step 4.

### Step 4: Reframe if Needed

If the user's intent was solution-shaped, surface it directly:

> "You've described what to build. Before we write requirements, let's make sure we have the goal right. Here's what I think you're actually trying to achieve: [outcome reframe]. Does that match your intent?"

Give the user a chance to correct the reframe. Don't proceed until they confirm the outcome statement is right.

### Step 5: Produce the Goal Statement

Write a structured goal statement:

```
Goal: [One sentence — what outcome changes and for whom]

Problem: [Why this matters now — what's broken, missing, or slow]

Success criteria:
- [Measurable indicator 1]
- [Measurable indicator 2]

Out of scope:
- [Thing that could easily be pulled in but shouldn't be]

Assumptions:
- [Load-bearing assumption 1]
- [Load-bearing assumption 2]
```

Show it to the user and ask: "Does this capture what you're trying to achieve?"

Revise until confirmed.

### Step 6: Persist (unless `--no-persist`)

**With `--linear`:**
```bash
# Create a Linear issue with the goal statement as the body
# Label: "goal" if the label exists, otherwise no label
# State: Backlog
```

Use the Linear MCP (`mcp__claude_ai_Linear__save_issue`) to create the issue. Set:
- Title: the Goal line (without the "Goal:" prefix)
- Description: the full goal statement in markdown
- Report the created issue URL.

**With `--append <file>` (or default `goals.md`):**
Append to the file:
```markdown
## [Goal title] — [date]

[Full goal statement]

---
```

If `goals.md` doesn't exist and the user hasn't passed `--no-persist`, ask: "Write this goal to `goals.md`?" before creating the file.

### Step 7: Handoff

End with:

```
Goal validated. Recommended next step:
  /prd-create     — write the PRD, ontology, and AERS against this goal
  /design-twice   — explore solution space before committing to an approach (if solution shape is uncertain)
  /issue-slices   — if you already have a PRD and want to slice it into tickets
  /prd-validate   — if a PRD already exists and needs validating
```

## CRITICAL: Do Not

- Do NOT accept a solution as a goal without surfacing the reframe
- Do NOT write requirements — that belongs in `/prd-create`
- Do NOT ask more than 3 clarifying questions
- Do NOT skip the stress-test reasoning even when the intent seems obvious — the reframe often surfaces in step 2
- Do NOT persist without confirmation when the default file doesn't exist

## Contract

- **Inputs:** plain-language description (optional arg or conversational). Flags: `--linear`, `--append <file>`, `--no-persist`.
- **Preconditions:** interactive session — this is a conversation, not a batch step. Never auto-invoke from non-interactive callers.
- **Outputs:** validated goal statement in the structured format above — this is the input `/prd-create --from` consumes. Optionally: a Linear issue or appended `goals.md` entry.
- **Postconditions:** user has confirmed the goal statement reflects the intended outcome. A persist artifact exists unless `--no-persist` was passed.
- **Failure modes:** user insists on a solution-shaped goal → document it as-is with a note flagging the risk; don't refuse to proceed. User says "just write the requirements" → surface that goal validation is fast and prevents wasted work, offer to skip if they insist.
