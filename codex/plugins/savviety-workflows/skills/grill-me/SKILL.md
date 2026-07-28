---
name: grill-me
description: "Stress-test a plan, design, architecture decision, PRD, or implementation approach by asking one focused challenge question at a time. Use when the user says 'grill me', wants assumptions challenged, or needs decision-tree gaps exposed before planning or coding. Does not implement changes or produce a full adversarial review report."
---

# Grill Me

Use this to pressure-test thinking before implementation.

## Workflow

1. Identify the decision, plan, or artifact being tested.
2. Read linked files or inspect the repo only when evidence would make the challenge more concrete.
3. Ask one question at a time. Do not dump a checklist.
4. After each answer, update the decision tree: settled facts, open risks, contradictions, and next branch.
5. Stop when the core decision is defensible, blocked by an explicit unknown, or the user asks to stop.

## Rules

- Challenge assumptions, tradeoffs, ownership, verification, rollback, security, data, UX, and operational impact.
- Prefer concrete repo evidence over abstract objections.
- Do not implement, rewrite the plan, or open a broad review unless the user changes the task.
- If the artifact needs a formal requirements review, hand off to `spec-review-adversarial`.
- If the result is ready for implementation planning, hand off to `execute-prd` or native Codex planning.
