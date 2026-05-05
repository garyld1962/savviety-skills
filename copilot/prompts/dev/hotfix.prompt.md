---
description: >-
  Apply a minimal, fast-tracked production fix with targeted verification and
  explicit scope control.
argument-hint: '[critical issue description]'
agent: 'agent'
tools:
  - execute
  - read
  - search
  - edit
  - codebase
---

# Hotfix

Use this prompt only for genuinely urgent production fixes.

Follow the skills:

- `.github/skills/repo-delivery/SKILL.md`
- `.github/skills/execution-environment/SKILL.md`

## Copilot-native usage

- Prefer the normal `/plan` -> `execute-plan` path for non-critical work.
- Keep the change minimal, targeted, and regression-aware.

## Security Quick Check

After the fix is applied and tests pass, **before committing**, run the security quick check from `.github/skills/review-engine/concept/security.md` — the **## Quick Pass** section.

Apply all 7 points to the hotfix diff:

1. No new secrets or credentials committed.
2. No injection vulnerabilities introduced (SQL, shell, NoSQL, etc.).
3. No auth or authorization bypasses.
4. Input validation remains intact.
5. No unsafe dynamic code execution.
6. No unescaped user content rendered as HTML.
7. No raw SQL string interpolation.

**Output one of:**

- **PASS:** "Security quick check: 7/7 clear." — proceed to commit.
- **FAIL:** Bulleted list of findings with file/line and which point failed. Halt and address findings before continuing. Override only with `--security-override <reason>`, with justification recorded in the PR body.

The check is diff-scoped (only what changed). This step is mandatory — do not skip it on a hotfix.
