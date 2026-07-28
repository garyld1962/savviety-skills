---
description: >-
  Audit a repository before planning or extending it. Produces an
  implemented/missing/duplicated/broken checklist without editing files.
  Use before writing plans when the codebase state is unknown. Do not
  use during implementation — use before planning.
argument-hint: '[path to audit]'
agent: agent
tools:
  - read
  - search
  - codebase
---

# Audit Existing Codebase

> **Built-in first:** For light codebase exploration, use `/research` directly. Use this prompt when you need a structured pre-planning audit with categorized output.

Produce a fast, structured inventory of what exists before code generation begins. This prevents plans from assuming greenfield state and surfaces duplicated contracts, missing tests, and broken wiring early.

## When to use

- Before drafting a plan from a PRD, prompt, or RFC.
- When the requirements source predates the repo and may be out of sync.
- When asked "what's already here?" before extending a package.

## When NOT to use

- The repo is provably greenfield (empty workspace stub) and the requirement is to scaffold from zero.
- You need to change code — this prompt is read-only by contract.

## Workflow

1. Read repo instructions (`copilot-instructions.md`) and the active requirements source, if any.
2. Use search and read tools to list source files, manifests, configs, schemas, migrations, and tests.
3. Identify implemented surfaces by package or module.
4. Compare current state to the requested scope.
5. Flag duplicated public contracts or constants, mismatched API or runtime types, missing validation, missing failure-path tests, and generated or native artifacts that may need runtime probes.
6. Classify external dependencies. Flag miscategorizations as test gaps — for example, a database mocked instead of substituted with an in-process alternative, internal services treated as true-external, or filesystem mocked instead of using an in-memory equivalent. These miscategorizations are coverage smells: tests pass but exercise the mock, not the real semantics.
7. Return an audit only; do not edit files.

## Output format

```markdown
## Existing State
- Package/module: implemented surfaces and key files

## Missing Or Partial
- Requirement or surface: evidence

## Duplicated Or Divergent Contracts
- Contract: locations and risk

## Test And Verification Gaps
- Gap: suggested focused verification

## Planning Implications
- Tasks or ownership constraints the execution plan should include
```

Keep output concise and cite file paths. If the repo is genuinely greenfield, say so and list the evidence.

## Constraints

- Do not edit files. The audit is read-only by contract.
- Do not propose fixes — only surface gaps. Fixes are the planner's job.
- Do not duplicate code review work. Audit is *what exists*, not *what is wrong with what exists*.
