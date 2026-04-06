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
- **File paths in findings**: Use EXACT paths verified by search. Do NOT cite "around line 42" --- cite the actual line number.
- **Fix recommendations**: Only recommend fixes using APIs, utilities, and patterns that ACTUALLY exist in the project. Do NOT recommend importing a utility that doesn't exist.
- **Documented behavior**: If code comments, CLAUDE.md, or copilot-instructions.md EXPLAIN why something works a certain way, that is mitigating context. Do NOT flag documented intentional behavior at the same severity as an accidental omission.

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

Read `.code-review/review-latest.json` --- scope determined by existing findings.

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
- Does it have `react`, `vue`, `svelte`, or `@angular/core` as a dependency? -> UI
- Does it have `express`, `fastify`, `koa`, or `hono` as a dependency? -> API
- Is it in a directory named `web`, `ui`, `frontend`, `app`? -> Likely UI
- Is it in a directory named `api`, `server`, `service`, `backend`? -> Likely API

When ambiguous: include the specialist. False negatives are worse than false positives.

---

## Step 4: Run Specialists

For each selected specialist, read the corresponding skill reference and apply its rules against each file in scope.

**While reviewing, note strengths.** As you examine each file, record solid patterns, good design decisions, and effective implementations. These go in the Strengths section of the report (Step 6). A review that only lists problems loses credibility with developers who know the codebase.

### Finding Schema --- MANDATORY

Every finding MUST conform to this schema:

```json
{
  "domain": "typescript-quality | api-patterns | ui-design-compliance | security | test-quality",
  "severity": "Blocker | High | Medium | Low | Info",
  "confidence": 0.50,
  "file": "src/services/auth.ts",
  "lineRange": "42-58",
  "title": "Max 120 chars - what is wrong",
  "rationale": "Why this is a problem - risk and impact",
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

### Severity Context Rules

Severity is not absolute. Consider:

- **Documented intentional behavior** drops severity by one level. If CLAUDE.md says "AUTH_TOKEN not set = dev mode" and the code implements exactly that, it is Medium (known tradeoff), not High (missing auth). The finding should note the documentation and explain the residual risk.
- **Deployment context matters.** A single-tenant personal tool behind K8s network policies has different risk than a public SaaS API. Do NOT apply enterprise SaaS severity to a personal-use system without justification.
- **Mitigating controls count.** If the code has a weakness but other layers compensate (e.g., network policies restrict access, env var gates the feature, upstream validation exists), note both the weakness AND the mitigation. Adjust severity accordingly.

### Example: Correct severity adjustment

```
AUTH_TOKEN fail-open is documented in CLAUDE.md as intentional dev mode, gated by
env var, and deploy-all.sh auto-generates the token for production. Residual risk:
misconfigured deployment could expose the API. Medium, not High.
```

### Example: INCORRECT severity adjustment

```
# WRONG: Ignoring mitigating context
AUTH_TOKEN fail-open. High severity. Recommendation: fail closed.
# <- Does not acknowledge documentation, env var gating, or deploy script behavior
```

### Confidence Calibration

| Range | Meaning |
|-------|---------|
| 0.90-1.00 | Certain --- clear pattern, no ambiguity |
| 0.75-0.89 | High --- strong signal |
| 0.60-0.74 | Moderate --- likely issue, needs judgment |
| 0.50-0.59 | Low --- possible issue, might be false positive |

**NEVER emit findings below 0.50 confidence.**

---

## Step 5: Deduplicate

1. Same file + overlapping lines + same domain -> keep higher severity
2. Same file + overlapping lines + different domains -> keep BOTH
3. Same pattern across multiple files -> collapse into ONE finding with file list
4. **Same root cause across client/server boundary -> merge into ONE finding citing both sides.** Example: if the server accepts tokens via query params AND the client sends tokens via query params, that is ONE finding ("tokens in query strings") referencing both the server endpoint and the client call site --- not two separate findings.
5. **Same root cause, different manifestations -> merge.** If a missing validation causes issues in both the API route and the UI form, that is one finding with two affected locations, not two findings.

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
- **WARN**: 0 Blockers AND >=1 High
- **FAIL**: >=1 Blocker (fixable)
- **ABORT**: >=1 Blocker that is system-breaking

Only `open` and `reopened` findings count. `fixed`, `verified`, `wont_fix` do not.

### Markdown report (full mode only)

Write to `docs/code-reviews/<date>-<scope>-<id>.md`. The report MUST include these sections in order:

1. **Header** --- date, mode, scope
2. **Severity summary** --- counts by level
3. **Files reviewed** --- every file examined
4. **Findings** --- ordered by severity (Blocker -> High -> Medium -> Low -> Info)
5. **Strengths** --- what the code does well (see below)
6. **Coverage notes** --- files reviewed with no findings (see below)
7. **Residual risks** --- areas not fully covered

### Strengths (REQUIRED in full mode)

List 3-5 specific, concrete things the code does well. These must be as specific as findings --- cite file:line, name the pattern, explain why it's good.

**Good strengths:**
- "Bearer token middleware (`api.ts:43-62`) is cleanly structured --- single extraction point, early return, consistent error format."
- "Extension manager reconnection logic (`extension-manager.ts:180-210`) handles session eviction gracefully with transparent retry."
- "Shared types package enforces a single source of truth for message schemas across brain, worker, and gateway."

**Bad strengths (do NOT write these):**
- "The code is generally well-written." --- too vague
- "Good use of TypeScript." --- says nothing
- "The project structure is clean." --- not specific

### Coverage Accountability

Every file in the "Files reviewed" list MUST have either:
- At least one finding referencing it, OR
- An explicit note in "Coverage notes" explaining why no issues were found

Example: "packages/shared/src/nats.ts --- no findings. Connection handling uses standard NATS patterns; reconnection is delegated to the client library."

Do NOT list a file as reviewed if you only skimmed it. If a file is in scope but you did not substantively review it, move it to a "Files in scope but not reviewed" list with a reason (e.g., "generated code", "no logic changes", "test-only changes").

---

## Step 7: Response

```
Code Review: <mode> -- <verdict>

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
1. [severity] <title> -- <file>:<line>
2. [severity] <title> -- <file>:<line>
3. [severity] <title> -- <file>:<line>

Strengths:
- <specific positive observation>
- <specific positive observation>

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
2. **Exact references only.** File paths, line numbers, code snippets --- all must be verified. Do NOT cite approximate locations.
3. **Confidence matters.** Do NOT pad findings to look thorough. Only report issues you are genuinely confident about.
4. **Actionable recommendations.** Every finding must include a concrete fix using APIs/patterns that exist in the project. "Consider improving this" is not a recommendation.
5. **No style wars.** Do NOT flag style preferences as Medium/High. Style issues are Low or Info at most.
6. **Acknowledge good work.** Every full review MUST include a Strengths section. A review that only lists problems is incomplete.
7. **Account for every file.** If you list a file as reviewed, justify why it has no findings or don't list it. Unexplained gaps erode trust.
8. **One root cause = one finding.** The same underlying issue seen from multiple angles (client/server, different files, different domains) is ONE finding with multiple locations --- not separate findings that inflate the count.
