---
name: review-foundations
description: Shared review principles for specialist compliance prompts in copilot-native.
---

# Review Foundations

Use this skill as the base layer for specialist review prompts such as:

- `review-api`
- `review-db`
- `review-design`
- `review-tests`

## Relationship to Copilot built-ins

- Built-in `/review` is the default quick review path.
- Specialist review prompts exist for targeted compliance checks with a narrower
  rubric and more explicit evidence gathering.

## Core review rules

- Read `.github/copilot-instructions.md` first.
- Match the project's own conventions before applying generic best practices.
- Read at least one reference implementation when the prompt depends on local
  patterns.
- Cite exact file and line references for findings.
- Prefer a small number of high-signal findings over a noisy audit dump.

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

## Guardrails

- Do not flag approximate locations.
- Do not treat style preferences as correctness failures.
- Do not review without first discovering the relevant local conventions.
