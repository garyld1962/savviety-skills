---
name: review-adversarial
description: Cross-model code review rubric for challenging changed code through skeptic, architect, and minimalist lenses after switching models in GitHub Copilot.
---

# Adversarial Review

Use this skill when running `#prompt:adversarial-review` or when manually asking
Copilot for a deliberate second-opinion pass after switching models with
`/model`.

## Relationship to Copilot built-ins

- Use built-in `/model` to switch to a different model before starting.
- Use built-in `/review` for the normal review path.
- Use this skill only when you want an explicitly adversarial challenge that
  stresses the changed code from a second model and writes a durable report.

## Core principle

> Find real problems. Do not validate the author's intent by default.

This workflow exists to create genuine cross-model scrutiny, not to produce a
friendlier version of `/review`.

## Scope rules

- Review only actual changed code unless the user explicitly names files,
  commits, or a PR scope.
- If no changed scope is visible, ask the user what to review.
- Read `.github/copilot-instructions.md` first so project conventions are not
  mistaken for defects.
- Determine and state the author's intent before rendering findings. If the
  intent is unclear, ask instead of guessing.

## Optional domain context

Read matching domain skills only when they exist and match the changed files.
Examples:

- `*.ts`, `*.tsx` -> language or TypeScript quality skill
- service/API code -> API pattern skill
- frontend UI -> design or accessibility skill
- tests -> test quality skill
- infrastructure or scripts -> security or platform skill

These skills sharpen the review. They do not replace the adversarial lens work.

## Lens selection

Select lenses by scope size:

| Size | Threshold | Lenses |
|------|-----------|--------|
| Small | < 50 lines, 1-2 files | Skeptic |
| Medium | 50-200 lines, 3-5 files | Skeptic + Architect |
| Large | 200+ lines or 5+ files | Skeptic + Architect + Minimalist |

### Skeptic

Challenge correctness and completeness:

- What breaks for a real input, state, or sequence?
- What claim is asserted without evidence?
- What error path is silently swallowed?
- What ordering or race assumption is unproven?
- Where is "works on my machine" substituting for verification?

### Architect

Challenge structural fitness:

- Does the design serve the stated goal or an assumed one?
- Where are responsibilities leaking across boundaries?
- What coupling will become expensive when requirements move?
- What assumptions about scale, concurrency, or ownership break first?

### Minimalist

Challenge necessity and complexity:

- What can be deleted without losing the goal?
- What abstraction exists for a single call site?
- Where is configuration added without a concrete second use case?
- What future-proofing is speculative rather than justified?

## Finding standard

Every finding must use this shape:

```markdown
- **[high/medium/low]** <description with exact file:line references>
  - Lens: Skeptic | Architect | Minimalist
  - Evidence: <code snippet or concrete failure scenario>
  - Recommendation: <specific action>
```

## Severity rules

| Rating | Criteria |
|--------|----------|
| `high` | correctness bug, security issue, data loss risk, or other ship blocker |
| `medium` | should-fix design flaw, missing edge case, or maintainability problem |
| `low` | useful but non-blocking note |

Severity must be backed by a concrete failure scenario. "This might be bad" is
not enough for `high`.

## Deduplication rules

- One root cause should produce one finding, even if it appears in multiple
  files.
- Do not split the same issue into client and server variants unless the fixes
  are meaningfully different.
- Prefer fewer, stronger findings over a long list of weak duplicates.

## Required report output

Persist the review under:

```text
docs/code-reviews/<YYYY-MM-DD>--<HHMMSS>--<scope>--adversarial-review--<5char-id>.md
```

Also maintain `docs/code-reviews/index.md`:

- append a one-line link if the file already exists
- otherwise create it with a simple bullet list of review links

## Report template

```markdown
# Adversarial Review

- **Date:** <YYYY-MM-DD HH:MM>
- **Scope:** <what was reviewed>
- **Lenses:** <selected lenses>

## Intent
<verified author intent>

## Verdict: PASS | CONTESTED | REJECT
<one-line summary>

## Findings
<ordered high -> medium -> low>

## Strengths
<2-5 concrete positives with file references when possible>

## Coverage Notes
<what was examined, what was not, and why>

## Lead Judgment
<accept or reject each major finding with one-line rationale>
```

## Verdict rules

- `PASS` when there are no high-severity findings
- `CONTESTED` when high-severity findings exist but the challenge is mixed or
  context materially lowers confidence
- `REJECT` when strong high-severity findings hold up across the selected lenses

## Examples

- **Small diff challenge:** Review a one-file bug fix through the Skeptic lens
  only, verify the author's intent, and emit a short persisted report with any
  concrete failure cases.
- **Large change-set challenge:** Review a multi-file feature through Skeptic,
  Architect, and Minimalist lenses, dedupe overlapping root causes, and persist
  a single adversarial report rather than scattered chat comments.

## Do Nots

- Do not invent intent.
- Do not review unchanged code by accident.
- Do not turn style preferences into correctness findings.
- Do not skip the persisted report.

## Closed Decisions

- This is a second-opinion workflow that runs after model switching, not the
  default review path.
- Review scope is limited to actual changed code unless the user explicitly
  broadens it.
- Findings must use the declared adversarial lenses and the fixed finding shape.
- The review result is persisted under `docs/code-reviews/` with the declared
  report template.
