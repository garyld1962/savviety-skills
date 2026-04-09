---
description: >-
  Stress-test a plan or design by interviewing the user one question at a time.
  Explores the codebase to answer questions it can resolve itself.
argument-hint: '[plan-file]'
agent: 'agent'
tools:
  - read
  - search
  - codebase
---

# Decision Stress Test

Interview the user about a plan or design until every decision branch is resolved.

## Steps

1. **Map decisions** — read the plan/design, identify architectural choices, unstated assumptions, and trade-offs.
2. **Walk the tree** — ask ONE question at a time. Provide your recommended answer. Wait for response. Follow up on new branches. Resolve dependencies in order (upstream first).
3. **Explore first** — before asking, check if the codebase can answer it (package.json, existing patterns, test files). Only ask questions needing human judgment.
4. **Summarize** — when all branches resolved, list decisions, confirmed assumptions, and open items.

## Rules

- One question at a time — never batch
- Provide your recommendation with every question
- Search the codebase before asking the user
- Stop when done — don't manufacture questions
