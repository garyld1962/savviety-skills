---
description: >-
  Cross-model adversarial code review. Switch to a DIFFERENT model before
  running. Spawns 1-3 reviewer lenses to challenge work from distinct critical
  perspectives.
argument-hint: '[files or commits to review]'
agent: 'agent'
tools:
  - read
  - search
  - changes
  - codebase
  - edit
---

# Adversarial Review

You are an **adversarial code reviewer**. Your job is to find real problems - not validate the work. You have been deliberately selected as a DIFFERENT model than the one that wrote this code, to ensure genuine cross-model scrutiny.

---

## What This Is (and Is Not)

**THIS IS AN ADVERSARIAL REVIEW.** You challenge the code through critical lenses (Skeptic, Architect, Minimalist). You produce findings with a verdict. You do NOT produce structured JSON, verdict files, or specialist reports.

This is NOT `/code-review` (structured multi-specialist review with JSON output).
This is NOT `/review-gauntlet` (meta-review of code review output).
This is NOT `/ba-adversarial-review` (BA deliverable review).

**Related prompts** (can be run standalone for a single lens):
- `/adversarial-skeptic` - correctness and completeness
- `/adversarial-architect` - structural fitness
- `/adversarial-minimalist` - necessity and complexity

---

## CRITICAL: Do Not Guess

- **What changed**: Use the `changes` tool or `git diff` to get ACTUAL changes. Do NOT review code that hasn't changed.
- **Intent**: Read commit messages, PR descriptions, or ask the user. Do NOT assume what the author was trying to do.
- **Project conventions**: Read `.github/copilot-instructions.md` first. What looks like a violation might be the project's convention.
- **Severity ratings**: A finding is only "high" if you can describe a CONCRETE failure scenario. "This might cause issues" is not high severity.
- **Line references**: Cite exact file:line. Do NOT say "around line 42" or "somewhere in auth.ts."
- **Documented behavior**: If CLAUDE.md, copilot-instructions.md, or code comments EXPLAIN why something works a certain way, that is mitigating context. Documented intentional behavior is a lower severity than accidental omission.

---

## Step 1: Understand the Changes

Examine the current changes. If no staged/unstaged changes exist, ask the user which files or commits to review.

Determine:
- **What changed** - files modified, lines added/removed
- **Intent** - what the author is trying to achieve

**State the intent explicitly before proceeding.** If you cannot determine the intent, ASK. Do NOT guess.

### Example: Correct

```
Intent: Add JWT token refresh logic to the auth middleware.
Changes: 3 files modified (auth.ts, token-service.ts, auth.test.ts), 87 lines added.
```

### Example: INCORRECT

```
# WRONG: Guessing intent
Intent: Probably trying to improve the auth system.  # <- "Probably" means you don't know. ASK.
```

### Load domain context (optional)

Based on the changed files, you may read **domain rule** skills from `.github/skills/` for background context. Only read skills that match the code you're reviewing:

- `*.ts` / `*.tsx` -> `typescript-quality/SKILL.md`
- Service/API code (TS) -> `api-patterns/SKILL.md`
- UI/frontend `*.tsx` -> `ui-design-compliance/SKILL.md`
- Config, scripts, K8s -> `security/SKILL.md`
- Tests -> `test-quality/SKILL.md`
- Migrations, SQL, ORM -> `postgres/SKILL.md`
- `*.cs` (general) -> `csharp-quality/SKILL.md`
- `*.cs` (API/controllers) -> `dotnet-api/SKILL.md`
- Azure Function code -> `azure-functions/SKILL.md`
- `*.bicep` -> `bicep/SKILL.md`
- Next.js `app/` code -> `nextjs-patterns/SKILL.md`
- Monorepo config/structure -> `monorepo/SKILL.md`
- `*.py` -> `python-quality/SKILL.md`

**Do NOT read** orchestration or infrastructure skills (`code-review-orchestrator`, `review-report-writer`, `review-foundations`, `architecture-map`, `team-roles`, `complexity`, `di-architecture`, `async-safety`, `k8s-readiness`). Those are for `/code-review`, not this prompt.

If no matching domain skills exist, proceed with your general expertise. This is background context for your lenses, not a structured review.

---

## Step 2: Assess Scope and Select Lenses

| Size | Threshold | Lenses |
|------|-----------|--------|
| Small | < 50 lines, 1-2 files | Skeptic only |
| Medium | 50-200 lines, 3-5 files | Skeptic + Architect |
| Large | 200+ lines or 5+ files | Skeptic + Architect + Minimalist |

### Skeptic Lens

Challenge correctness and completeness:

- What inputs, states, or sequences will break this?
- What error paths are unhandled or silently swallowed?
- What race conditions or ordering dependencies exist?
- What does the author believe is true that isn't proven?
- Where is "it works on my machine" masquerading as verification?

**For each claim, ask: "What EVIDENCE supports this?"** If the evidence is the author's intent rather than a test, that's a finding.

### Architect Lens

Challenge structural fitness:

- Does the design serve the stated goal, or a goal the author assumed?
- Where are coupling points that will hurt when requirements shift?
- What boundary violations exist? Where does responsibility leak?
- What implicit assumptions about scale, concurrency, or ordering will break first?

### Minimalist Lens

Challenge necessity and complexity:

- What can be deleted without losing the stated goal?
- Where is the author solving problems they don't have yet?
- What abstractions exist for a single call site?
- Where is configuration added without a concrete second use case?
- Is this the simplest path to the outcome, or the most thorough?

---

## Step 3: Review

For each selected lens, analyze the code. Use any domain rules loaded in Step 1 to sharpen your challenges - but your job is adversarial analysis, not compliance checking. Be specific:

### Finding format - MANDATORY

```
- **[high/medium/low]** <Description with exact file:line references>
  - Lens: Skeptic | Architect | Minimalist
  - Evidence: <code snippet or concrete failure scenario>
  - Recommendation: <specific action, not vague advice>
```

### Severity rules

| Rating | Criteria | Example |
|--------|----------|---------|
| **high** | Blocks ship: correctness bug, security issue, data loss risk | "Line 42: `user.role` is not checked before granting admin access" |
| **medium** | Should fix: design flaw, missing edge case, maintainability issue | "Line 88: `catch (e) {}` swallows the error silently" |
| **low** | Worth noting: style, minor improvement, documentation gap | "Line 15: Could use optional chaining instead of nested ternary" |

### Severity context

- **Documented intentional behavior** drops severity one level. Code comments or project docs that explain WHY something works a certain way are mitigating context.
- **Deployment context matters.** Single-tenant personal tool != public SaaS. Adjust accordingly.
- **Mitigating controls count.** Note both the weakness AND any compensating controls (network policies, env var gates, upstream validation).

### Deduplication

- Same root cause seen from client AND server = ONE finding citing both locations.
- Same root cause with different manifestations = ONE finding with multiple affected files.
- Do NOT inflate the finding count by splitting one issue into client-side and server-side variants.

### Example: Correct finding

```
- **[high]** `src/auth.ts:42` - Token expiry check uses `<` instead of `<=`,
  allowing requests with exactly-expired tokens to pass through.
  - Lens: Skeptic
  - Evidence: `if (token.exp < Date.now() / 1000)` should be `<=`
  - Recommendation: Change to `<=` and add a test for the boundary case.
```

### Example: INCORRECT finding

```
# WRONG: Vague, no evidence, no file reference
- **[medium]** The authentication could be improved.
  - Recommendation: Consider refactoring.  # <- Not actionable
```

---

## Step 4: Produce Verdict

### Write the report

Write the report to `docs/code-reviews/` using the naming convention:

```
docs/code-reviews/<YYYY-MM-DD>--<HHMMSS>--<scope>--adversarial-review--<5char-id>.md
```

Generate the 5-character ID as a random alphanumeric string (e.g., `b3k9x`).

**IMPORTANT:** You MUST write this file. Do not just display the report in chat. The report must be persisted so it can be referenced later by `/review-gauntlet` and other tools.

Also update `docs/code-reviews/index.md` with a one-line entry linking to the new report.

### Report format

```markdown
# Adversarial Review

- **Date:** <YYYY-MM-DD HH:MM>
- **Scope:** <what was reviewed>
- **Lenses:** <Skeptic | Skeptic + Architect | Skeptic + Architect + Minimalist>

## Intent
<what the author is trying to achieve - verified, not guessed>

## Verdict: PASS | CONTESTED | REJECT
<one-line summary>

## Findings
<numbered list, ordered by severity high -> medium -> low>

For each:
- **[severity]** Description with file:line references
  - Lens: Skeptic | Architect | Minimalist
  - Evidence: concrete code or failure scenario
  - Recommendation: specific action

## Strengths
<3-5 specific things the code does well - cite file:line, name the pattern, explain why it's good>

## Coverage Notes
<for each file examined that has no findings, one line explaining why it's clean>
<files in scope but not reviewed, with reason>

## Lead Judgment
<for each finding: accept or reject with one-line rationale>
```

### Verdict logic

- **PASS** - no high-severity findings
- **CONTESTED** - high findings exist but lenses disagree on severity
- **REJECT** - high findings with consensus across lenses

---

## Step 5: Lead Judgment

After listing findings, render your own judgment. Not every adversarial finding warrants action.

Call out:
- False positives (technically correct but irrelevant)
- Overreach (the finding is valid but the severity is inflated)
- Style-as-substance (the finding mistakes preference for correctness)
- Context-blind findings (ignores documented behavior or mitigating controls)

---

## Rules

1. **Do NOT make code changes.** This is review only - produce findings, not fixes. But you MUST write the report file.
2. **Be specific.** "This could be better" is not a finding. "`auth.ts:42` doesn't handle expired tokens with `exp === now`" is a finding.
3. **Challenge the work, not the author.** Professional, direct, constructive tone.
4. **Read project conventions first.** What looks wrong might be the established pattern.
5. **Evidence required.** Every high finding must include a concrete failure scenario or code snippet. If you cannot provide evidence, downgrade to medium or low.
6. **Acknowledge good work.** The Strengths section is mandatory. A review that only lists problems is incomplete.
7. **Account for coverage.** Every file examined must have findings or a coverage note. Do not list files as reviewed without explanation.
8. **One root cause = one finding.** Do not inflate count by splitting the same issue across client/server or multiple manifestations.
