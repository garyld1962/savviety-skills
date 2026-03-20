---
description: >-
  Multi-specialist code review: full review, quick check, or verify fixes.
  Covers TypeScript quality, API patterns, security, test quality, and UI
  compliance.
argument-hint: '[full | quick | verify] [--scope=package|team|file --target=<path>]'
agent: 'agent'
tools:
  - read
  - search
  - codebase
  - execute
  - changes
  - edit
---

# Code Review System

Automated code review with structured findings, severity ratings, and actionable recommendations. Adapts to any TypeScript monorepo.

## When to Use

| Moment | Mode | Action |
|--------|------|--------|
| Mid-development, after a logical chunk | `quick` | Catch issues early |
| Feature is complete | `full` (default) | Full quality assurance |
| After fixing reported issues | `verify` | Targeted re-check |

---

## CRITICAL: Do Not Guess

- **Project conventions**: READ `.github/copilot-instructions.md` before reviewing. The project may have specific patterns that override general best practices.
- **Shared package identity**: DETECT the shared types package from workspace config. Do NOT assume it's called `shared` or `@project/shared`.
- **UI vs API packages**: Check directory structure and `package.json` to determine if a package is UI or backend. Do NOT classify based on the directory name alone.
- **Finding severity**: Only report findings you are confident about. If confidence is below 0.50, do NOT emit the finding. False positives waste developer time.
- **File paths in findings**: Use EXACT paths verified by search. Do NOT cite "around line 42" — cite the actual line number.
- **Fix recommendations**: Only recommend fixes using APIs, utilities, and patterns that ACTUALLY exist in the project. Do NOT recommend importing a utility that doesn't exist.

---

## Review Modes

### Full Review (default)

1. Get all files changed since branching from default branch
2. Run ALL applicable specialists
3. Generate markdown report with findings
4. Create verdict JSON file
5. Return summary

### Quick Review

1. Get only uncommitted changes (`git diff --name-only`)
2. Run only typescript-quality and security specialists
3. Write verdict JSON (no markdown report)
4. Return summary with top issues

### Verify Fixes

1. Read `.code-review/review-latest.json`
2. Re-check ONLY findings marked `"fixed"`
3. Update each to `"verified"` (resolved) or `"reopened"` (still present)
4. Recalculate verdict

---

## Step 1: Project Discovery (Run Once)

### 1a. Read project conventions

```
Read: .github/copilot-instructions.md
```

Extract: coding conventions, naming rules, error handling patterns, import rules, security requirements.

### 1b. Detect workspace structure

```bash
cat pnpm-workspace.yaml 2>/dev/null || cat package.json | grep -A 10 '"workspaces"'
```

### 1c. Identify shared package

Check workspace config for a package named `shared`, `common`, `core`, or read `.code-review/config.json` `sharedPackage` field.

### 1d. Load review config (optional)

Read `.code-review/config.json` if it exists for team mappings, specialist overrides, custom scope rules.

---

## Step 2: Gather Scope

### Full mode

```bash
# Detect default branch
DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
[ -z "$DEFAULT" ] && DEFAULT=$(git show-ref --verify --quiet refs/remotes/origin/master 2>/dev/null && echo master || echo main)

git diff origin/$DEFAULT --name-only
```

### Quick mode

```bash
git diff --name-only
```

### Verify mode

Read `.code-review/review-latest.json` — scope determined by existing findings.

---

## Step 3: Select Specialists

Based on files in scope:

| File Pattern | Specialist | Reference |
|-------------|-----------|-----------|
| `*.ts`, `*.tsx` (any) | typescript-quality | [skill](../../skills/typescript-quality/SKILL.md) (always) |
| Service/API packages (non-UI) | api-patterns | [skill](../../skills/api-patterns/SKILL.md) |
| `*.tsx` in UI/frontend packages | ui-design-compliance | [skill](../../skills/ui-design-compliance/SKILL.md) |
| Service code, config, K8s, scripts | security | [skill](../../skills/security/SKILL.md) (always) |
| `*.test.ts` or source missing test companions | test-quality | [skill](../../skills/test-quality/SKILL.md) |
| Migrations, schema defs, SQL/ORM code | postgres | [skill](../../skills/postgres/SKILL.md) |
| `*.cs` (any) | csharp-quality | [skill](../../skills/csharp-quality/SKILL.md) |
| `*.cs` (API controllers, minimal APIs) | dotnet-api | [skill](../../skills/dotnet-api/SKILL.md) |
| Azure Function classes | azure-functions | [skill](../../skills/azure-functions/SKILL.md) |
| `*.bicep` | bicep | [skill](../../skills/bicep/SKILL.md) |
| Next.js `app/` routes, layouts, pages | nextjs-patterns | [skill](../../skills/nextjs-patterns/SKILL.md) |
| `*.py` | python-quality | [skill](../../skills/python-quality/SKILL.md) |

**Quick mode:** Only typescript-quality/csharp-quality (by language) + security, regardless of file patterns.

**Verify mode:** Specialists determined by the `domain` field of `"fixed"` findings.

### How to determine UI vs API packages

Read the package's `package.json` and check:
- Does it have `react`, `vue`, `svelte`, or `@angular/core` as a dependency? → UI
- Does it have `express`, `fastify`, `koa`, or `hono` as a dependency? → API
- Is it in a directory named `web`, `ui`, `frontend`, `app`? → Likely UI
- Is it in a directory named `api`, `server`, `service`, `backend`? → Likely API

When ambiguous: include the specialist. False negatives are worse than false positives.

---

## Step 4: Run Specialists

For each selected specialist, read the corresponding skill reference and apply its rules against each file in scope.

### Finding Schema — MANDATORY

Every finding MUST conform to this schema:

```json
{
  "domain": "typescript-quality | api-patterns | ui-design-compliance | security | test-quality",
  "severity": "Blocker | High | Medium | Low | Info",
  "confidence": 0.50,
  "file": "src/services/auth.ts",
  "lineRange": "42-58",
  "title": "Max 120 chars — what is wrong",
  "rationale": "Why this is a problem — risk and impact",
  "recommendation": "Concrete fix: exactly what to change",
  "evidence": "code snippet showing the issue",
  "suggestedPatch": "unified diff (optional)",
  "ruleRef": "reference to project convention (optional)"
}
```

### Severity Calibration

| Level | When to Use | Examples |
|-------|------------|---------|
| **Blocker** | Security vulnerability, data loss, guaranteed crash | SQL injection, unhandled null in production path |
| **High** | Significant bug, pattern violation, missing functionality | Missing error handling on network call, wrong return type |
| **Medium** | Code quality issue, minor pattern deviation | Unused variable, inconsistent naming |
| **Low** | Style preference, minor optimization | Could use optional chaining, verbose code |
| **Info** | Observation, positive feedback | "Good use of generics here" |

### Confidence Calibration

| Range | Meaning |
|-------|---------|
| 0.90-1.00 | Certain — clear pattern, no ambiguity |
| 0.75-0.89 | High — strong signal |
| 0.60-0.74 | Moderate — likely issue, needs judgment |
| 0.50-0.59 | Low — possible issue, might be false positive |

**NEVER emit findings below 0.50 confidence.**

---

## Step 5: Deduplicate

1. Same file + overlapping lines + same domain → keep higher severity
2. Same file + overlapping lines + different domains → keep BOTH
3. Same pattern across multiple files → collapse into ONE finding with file list

### Finding caps

- file scope: max 25 findings
- changeset scope: max 30 findings
- package scope: max 30 findings
- team scope: max 40 findings

---

## Step 6: Write Output

### Verdict JSON

Write to `.code-review/review-latest.json`:

```json
{
  "reviewId": "<8-char-hex>",
  "timestamp": "<ISO 8601>",
  "scope": "changeset | package | team | file",
  "target": "origin/main..HEAD",
  "mode": "full | quick | verify",
  "verdict": "PASS | WARN | FAIL | ABORT",
  "summary": { "blocker": 0, "high": 0, "medium": 0, "low": 0, "info": 0 },
  "reportPath": "docs/code-reviews/<date>-<scope>-<id>.md",
  "findings": []
}
```

### Verdict Logic

- **PASS**: 0 Blockers AND 0 High (open/reopened)
- **WARN**: 0 Blockers AND ≥1 High
- **FAIL**: ≥1 Blocker (fixable)
- **ABORT**: ≥1 Blocker that is system-breaking

Only `open` and `reopened` findings count. `fixed`, `verified`, `wont_fix` do not.

### Markdown report (full mode only)

Write to `docs/code-reviews/<date>-<scope>-<id>.md`. Include all findings ordered by severity.

---

## Step 7: Response

```
Code Review: <mode> — <verdict>

Scope: <N> files across <M> packages
Specialists: <list>

| Severity | Count |
|----------|-------|
| Blocker | N |
| High | N |
| Medium | N |
| Low | N |
| Info | N |

Top findings:
1. [severity] <title> — <file>:<line>
2. [severity] <title> — <file>:<line>
3. [severity] <title> — <file>:<line>

Verdict file: .code-review/review-latest.json
Report: <report-path> (full mode only)
```

---

## Developer Workflow

| Verdict | Action |
|---------|--------|
| **PASS** | Create PR |
| **WARN** | Fix High findings (required), Medium (recommended) |
| **FAIL** | Fix all Blockers, then High, then run verify mode |
| **ABORT** | Stop work. Needs human review of the architectural issue |

---

## Rules

1. **Read conventions first.** Project docs override general best practices. A pattern that looks wrong might be intentional.
2. **Exact references only.** File paths, line numbers, code snippets — all must be verified. Do NOT cite approximate locations.
3. **Confidence matters.** Do NOT pad findings to look thorough. Only report issues you are genuinely confident about.
4. **Actionable recommendations.** Every finding must include a concrete fix using APIs/patterns that exist in the project. "Consider improving this" is not a recommendation.
5. **No style wars.** Do NOT flag style preferences as Medium/High. Style issues are Low or Info at most.
