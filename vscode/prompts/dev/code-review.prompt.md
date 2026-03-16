---
description: "Run a multi-specialist code review: full review, quick check, or verify fixes. Specialists cover TypeScript quality, API patterns, security, test quality, and UI compliance."
argument-hint: "Mode: full, quick, or verify"
---

# Code Review System

Automated code review with structured findings, severity ratings, and actionable recommendations. Project-agnostic — adapts to any TypeScript monorepo.

## When to Use

| Moment | Mode | Action |
|--------|------|--------|
| Mid-development, after a logical chunk | Quick review | Catch issues early |
| Feature is complete | Full review | Full quality assurance |
| After fixing reported issues | Verify fixes | Targeted re-check |

## Review Modes

### Full Review
1. Analyze all files changed since branching from main
2. Run all applicable specialists
3. Generate markdown report with findings
4. Create verdict JSON file
5. Return summary

### Quick Review
1. Analyze only uncommitted changes
2. Run only `typescript-quality` and `security` specialists
3. Write verdict JSON (no markdown report)
4. Return summary with top issues

### Verify Fixes
1. Re-check only findings marked "fixed"
2. Update each to "verified" (resolved) or "reopened" (still present)
3. Recalculate verdict

## Project Discovery (Run Once)

1. **Read `.github/copilot-instructions.md`** — learn project conventions
2. **Read `.code-review/config.json`** if it exists — get team mappings, specialist toggles
3. **Read workspace config** — `pnpm-workspace.yaml` or root `package.json` `workspaces` field
4. **Identify shared package**

## Specialist Selection

Based on files in scope:

| File Pattern | Specialist |
|-------------|-----------|
| `*.ts`, `*.tsx` (any) | [typescript-quality](../../skills/typescript-quality/SKILL.md) (always) |
| Service/API packages | [api-patterns](../../skills/api-patterns/SKILL.md) |
| `*.tsx` in UI packages | [ui-design-compliance](../../skills/ui-design-compliance/SKILL.md) |
| Service code, config, K8s, scripts | [security](../../skills/security/SKILL.md) (always) |
| `*.test.ts` or missing tests | [test-quality](../../skills/test-quality/SKILL.md) |

Quick mode: Only typescript-quality + security.

## Finding Schema

Every finding MUST conform to:

```json
{
  "domain": "typescript-quality | api-patterns | ui-design-compliance | security | test-quality",
  "severity": "Blocker | High | Medium | Low | Info",
  "confidence": 0.50-1.00,
  "file": "src/services/auth.ts",
  "lineRange": "42-58",
  "title": "Max 120 chars",
  "rationale": "Why this is a problem — risk and impact",
  "recommendation": "Concrete fix instruction",
  "evidence": "code snippet",
  "suggestedPatch": "unified diff (optional)",
  "ruleRef": "copilot-instructions.md reference (optional)"
}
```

## Severity Calibration

| Level | Description | Action |
|-------|------------|--------|
| **Blocker** | Security vulnerability, data loss, guaranteed crash | Must fix before merge |
| **High** | Significant bug, pattern violation, missing functionality | Should fix before merge |
| **Medium** | Code quality issue, minor pattern deviation | Fix recommended |
| **Low** | Style preference, minor optimization | Fix at convenience |
| **Info** | Observation, suggestion, positive feedback | Optional |

## Confidence Calibration

| Range | Meaning |
|-------|---------|
| 0.90-1.00 | Certain — clear pattern, no ambiguity |
| 0.75-0.89 | High confidence — strong signal |
| 0.60-0.74 | Moderate — likely issue, needs judgment |
| 0.50-0.59 | Low confidence — possible issue, might be false positive |

Never emit findings below 0.50 confidence.

## Deduplication Rules

1. Same file + overlapping lines + same domain → keep higher severity
2. Same file + overlapping lines + different domains → keep BOTH
3. Same pattern across multiple files → collapse into ONE finding with file list

## Verdict Logic

- **PASS**: 0 Blockers AND 0 High
- **WARN**: 0 Blockers AND >=1 High
- **FAIL**: >=1 Blocker (fixable)
- **ABORT**: >=1 Blocker (system-breaking)

Only findings with status `open` or `reopened` count toward verdict.

## Finding Status Lifecycle

| Status | Set by | Meaning |
|--------|--------|---------|
| `open` | Skill | New or unaddressed |
| `fixed` | Developer | Claims resolved |
| `verified` | Skill (verify) | Confirmed fix works |
| `reopened` | Skill (verify) | Issue still present |
| `wont_fix` | Developer | False positive or intentional |

## Verdict JSON Schema

Stored in `.code-review/review-latest.json`:

```typescript
interface ReviewVerdict {
  reviewId: string;          // 8-char hex
  timestamp: string;         // ISO 8601
  scope: 'changeset' | 'package' | 'team' | 'file';
  target: string;            // e.g., "origin/main..HEAD"
  mode: 'full' | 'quick' | 'verify';
  verdict: 'PASS' | 'WARN' | 'FAIL' | 'ABORT';
  summary: { blocker: number; high: number; medium: number; low: number; info: number };
  reportPath: string;
  findings: ReviewFinding[];
}
```

## Developer Workflow

| Verdict | Action |
|---------|--------|
| **PASS** | Proceed to create PR |
| **WARN** | Fix all High (required), Medium (recommended) |
| **FAIL** | Fix all Blockers, then High, then run verify |
| **ABORT** | Stop work, write `.code-review/abort-reason.md`, wait for intervention |

## Report Output

Reports go to `docs/code-reviews/{date}-{scope}-{id}.md`.

## Project Configuration (Optional)

`.code-review/config.json`:
```json
{
  "teams": { "team-1": { "name": "Core", "paths": ["services/brain"] } },
  "sharedPackage": "packages/shared",
  "specialists": {
    "api-patterns": { "enabled": true, "extraScope": ["lib/server/**"] }
  }
}
```
