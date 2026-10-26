---
name: plan-format
description: "Canonical plan document format produced by /execute-prd and consumed by /execute-plan's runtime workflow. Defines frontmatter, task metadata (depends_on, milestone_end), and mechanical acceptance blocks. Not user-invokable."
user-invocable: false
internal: true
kind: reference
---

# Plan Format (compiler ↔ runtime contract)

A plan is a markdown file. The runtime workflow parses it via an
agent with a JSON schema; this document is the source of truth both
for the author (execute-prd step 7) and the parser prompt
(run-plan.mjs `PLAN_SCHEMA` agent).

## Frontmatter (YAML, required)

    ---
    slug: <kebab-case plan id>
    source_prd: <path or ADO/Linear ref>
    intent: <one-sentence goal, verbatim usable as pr_description>
    type: bug | feature | refactor | infra
    ---

## Body structure

- H1 title.
- `**Source:**` line referencing the original artefact.
- Optional `## Closed Decisions` — bullets; each is tablestakes for
  the runtime (workers may not re-litigate them).
- One or more `## Task N: <title>` sections, N unique and ascending.

## Task section metadata (replaces the old ## Waves / lane tables)

Each task section starts with a fenced metadata block:

    ```yaml
    depends_on: []          # task numbers that must complete first
    write_scope:            # globs this task may modify
      - src/api/**
    milestone_end: false    # true → runtime runs a review gate after it
    ```

Dependency structure IS the parallelism declaration: tasks whose
`depends_on` are all satisfied and whose `write_scope` globs are
mutually disjoint run as one parallel group in isolated worktrees.
No separate `## Waves` section, no lane registry, no max-team rule —
the runtime computes groups and caps concurrency itself.

Single-owner surfaces (root manifests, lockfiles, shared types,
migrations, generated files) must appear in exactly one task's
`write_scope`. Overlap between two dependency-independent tasks is a
validation error (execute-prd step 8 checks it; the runtime re-checks
and serialises the pair if found).

## Acceptance blocks

Each task ends with `**Acceptance:**` bullets. Every bullet must be
mechanical: a command that exits 0, or an observable with its exact
expected value. Prose like "works correctly" is a validation error.

## Milestones

`milestone_end: true` on a task triggers the runtime's review gate
after that task's group completes. If no task sets it, the runtime
treats the final task as the only milestone.
