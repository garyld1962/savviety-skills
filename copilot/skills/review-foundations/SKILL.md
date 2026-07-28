---
name: review-foundations
description: Legacy compatibility bridge for specialist review prompts. The primary shared review logic now lives in review-engine.
---

# Review Foundations

This skill exists as a compatibility bridge for older specialist prompts such as:

- `review-api`
- `review-db`
- `review-design`
- `review-tests`

For new work, prefer:

- built-in `/review` for the quick/default path
- `domain-review` for deeper defect-focused review
- `professional-review` for senior engineering judgment
- `.github/skills/review-engine/SKILL.md` as the shared domain engine

## Relationship to Copilot built-ins

- Built-in `/review` is the default quick review path.
- Specialist review prompts are now thin launchers into the shared review engine
  with extra domain emphasis, not separate review systems.

## Core review rules

- Read `.github/copilot-instructions.md` first.
- Match the project's own conventions before applying generic best practices.
- Read at least one reference implementation when the prompt depends on local
  patterns.
- Cite exact file and line references for findings.
- Prefer a small number of high-signal findings over a noisy audit dump.
- Distinguish direct code defects from broader professional-engineering concerns.

## Finding shape

```markdown
1. **[high/medium/low]** `file:line` — <issue>
   - Expected: <project or domain convention>
   - Found: <what the code does>
   - Fix: <specific action>
```

## Verdict guidance

- `PASS` when no material violations are found
- `WARN` when issues exist but the code is still broadly aligned
- `FAIL` when the code clearly violates required project or domain conventions

## Examples

- **Targeted API review:** Read the changed service files plus one local
  reference implementation, then report only the concrete contract, validation,
  or auth issues with exact file and line references.
- **Targeted test review:** Use the repo's existing test style as the baseline,
  then flag only the real isolation, determinism, or coverage defects rather
  than general formatting preferences.

## Guardrails

- Do not flag approximate locations.
- Do not treat style preferences as correctness failures.
- Do not review without first discovering the relevant local conventions.
- Do not use this compatibility layer as a substitute for the shared
  `review-engine` domain selection model.

## Do Nots

- Do not emit a repo-wide audit when the invoking prompt asked for a narrower
  specialist pass.
- Do not turn this bridge skill into a second review controller with its own
  domain-selection logic.

## Closed Decisions

- This skill is a compatibility bridge, not the primary review system.
- Built-in `/review` remains the default quick path.
- `review-engine` owns domain selection and orchestration for deeper review
  lanes.
- Findings must use exact locations and high-signal evidence.
