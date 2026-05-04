---
name: audit-existing
description: "Audit an existing repository or package before planning or extending it. Use when a prompt asks to inspect current state first, when requirements may not match the implementation, or before generating an execution plan from a PRD/prompt/RFC. Produces a concise implemented/missing/duplicated/broken checklist; does not edit files."
---

# audit-existing

Purpose: produce a fast, structured inventory of what exists before code
generation begins. This prevents plans from assuming greenfield state and
surfaces duplicated contracts, missing tests, and broken wiring early.

## When to Use

- Before `/execute-prd` drafts a plan from a PRD/prompt/RFC.
- When the requirements source predates the repo and may be out of sync.
- When a user asks "what's already here?" before extending a package.

## When NOT to Use

- The repo is provably greenfield (an empty workspace stub) and the
  requirement is to scaffold from zero — `/execute-prd` will say so and
  skip the audit.
- You need to *change* code — this skill is read-only by contract.

## Workflow

1. Read repo instructions (`CLAUDE.md`) and the active requirements
   source, if any.
2. List source files, manifests, configs, schemas, migrations, and tests.
3. Identify implemented surfaces by package/module.
4. Compare current state to the requested scope.
5. Flag duplicated public contracts/constants, mismatched API/runtime
   types, missing validation, missing failure-path tests, and
   generated/native artifacts that may need runtime probes.
6. Return an audit only; do not edit files.

## Output

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

Keep it concise and cite file paths. If the repo is genuinely greenfield,
say so and list the evidence.

## Things you must not do

- Do not edit files. The audit is read-only by contract.
- Do not propose fixes — only surface gaps. Fixes are the planner's job.
- Do not duplicate work `/code-review` does. Audit is *what exists*, not
  *what's wrong with what exists*.
