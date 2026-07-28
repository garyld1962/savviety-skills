---
description: >-
  Audit an older or dormant codebase against current GitHub Copilot workflow
  capability and produce a prescriptive within-stack refactor plan. Use for
  phrases like "modernize this codebase", "refresh the code", "what would this
  look like today", "AI-time refresh", or "modernization audit". Focus on
  structure, boundaries, types, error handling, tests, infra organization, and
  dead code. Do not recommend framework changes, language switches, public API
  rewrites, dependency-upgrade campaigns, or broad redesigns.
argument-hint: '[path] [--report-only] [--handoff] [--out=path] [--max-moves=N] [--theme=name]'
tools:
  - read
  - search
  - codebase
  - edit
---

# /modernize — Code Modernization Audit

> **Built-in first:** use direct edits for small cleanup and built-in `/plan`
> for ordinary refactor planning. Use this prompt when you want a deliberate
> modernization audit that produces a governed refactor plan.

Follow the skills:

- `.github/skills/modernization-rubric/SKILL.md`
- `.github/skills/copilot-platform-playbook/SKILL.md`

## Purpose

Read an existing codebase holistically and produce a short, execution-ready
refactor plan calibrated to what current Copilot workflows can safely carry
out. This is a planning front end for the `execute-prd` prompt with
`--type=refactor`, not a free-form report generator and not an automatic code
rewrite.

## When to Use

- A project has been dormant for months or was last worked on with weaker
  agent tooling.
- The code shows older-agent patterns: excessive defensive branching, weak
  typing, kitchen-sink utilities, mixed concerns, or shallow tests.
- The user asks to modernize, refresh, revisit, or ask what the code would
  look like with today's tooling.
- The desired output is a refactor plan that can be reviewed first or handed
  to `execute-prd`.

## When NOT to Use

- The user has a specific bug or feature request. Handle that directly or use
  `execute-prd`.
- The task is dependency-driven modernization, CVEs, lockfile churn, or
  package upgrade work. Use `dep-audit` and `dep-migrate`.
- The project likely needs a new framework, language, database, or public API
  shape. Surface that only as an out-of-scope appendix note.
- The repo is tiny, roughly under 500 LOC. Recommend direct edits or a focused
  simplification instead.
- The user wants a prompt/skill portfolio audit rather than codebase
  modernization. Use `skill-audit`.

## Scope Boundaries

**Stay strictly within the current platform and stack.**

- **Will recommend:** structural refactors, type improvements, module
  reorganization, error-handling sharpening, test depth, infra/config cleanup,
  naming clarity, dead-code removal.
- **Will not recommend:** framework swaps, language switches, public API
  rewrites, database replacements, dependency-upgrade campaigns, or broad
  redesigns.

If the repo overwhelmingly wants a different framework or architecture, record
that as an `out-of-scope-finding` in the appendix. Do not turn it into a
primary-plan move.

## Arguments

| Argument | Description |
|---|---|
| `[path]` | Codebase root. Default: current working directory. |
| `--report-only` | Write the modernization plan and stop. This is the default posture unless the user clearly asked for execution. |
| `--handoff` | After writing the plan, run `execute-prd --type=refactor <plan-path>`. Use only when the user clearly asked to continue into execution. |
| `--out=<path>` | Output path. Default: `docs/plans/modernization-<YYYYMMDD>.md`. |
| `--max-moves=<N>` | Cap primary plan moves. Default: 10. |
| `--theme=<name>` | Restrict to one or more themes: `abstraction`, `separation`, `types`, `errors`, `tests`, `infra`. |

## Workflow

### 1. Detect project shape

Use the modernization-rubric skill to classify:

- primary language
- project type
- size class
- test coverage signal
- visible architecture pattern

Halt on tiny repos and on very large repos where a per-package audit is safer.

### 2. Establish the descriptive baseline

Run the `audit-existing` prompt for current-state evidence. Carry its findings
forward; do not duplicate the entire audit in this prompt.

### 3. Sample-read by signal category

Use the modernization-rubric skill's sample-read strategy:

- breadth
- depth
- boundaries
- public surface
- hotspots
- test parity

Do not exhaustive-read large repos. Stop when the sampling budget is sufficient
for synthesis.

### 4. Apply the "what is newly feasible" overlay

For each finding, ask whether the main blocker used to be tool capability:

- multi-file consistent renames
- type-system repair at scale
- cross-module data-flow cleanup
- safer broad test-assisted refactors

If yes, raise its priority. If the blocker is a project constraint, keep it as
lower-priority or appendix-only. This is the "AI-time refresh" filter.

### 5. Synthesize candidate moves

Group findings into themes:

- Abstraction
- Separation of concerns
- Types
- Errors
- Tests
- Infra

For each move capture:

- representative `file:line` evidence (3 examples max)
- current state
- proposed state
- impact
- ease
- blast radius
- rationale
- mechanically verifiable acceptance criteria

### 6. Cull aggressively

Use the modernization-rubric skill's cull tests:

1. senior engineer test
2. stylistic-preference test
3. within-stack test
4. blast-radius vs. impact test
5. cap test

Prefer a short list of high-confidence moves over a long catalog of taste
calls.

### 7. Emit the refactor plan

Write the plan to `--out` in a shape consumable by `execute-prd --type=refactor`:

```md
---
slug: modernization-<YYYYMMDD>
source_prd: (this report)
intent: refactor
type: refactor
---

# Modernization Plan — <YYYY-MM-DD>

**Codebase:** <path>
**Shape:** <type>, <size class>, <language>
**Moves:** <N>
**Generated by:** /modernize

## Summary

| Theme | Moves | Top finding |
|---|---|---|
| Abstraction | N | <one-line> |

## Closed Decisions

- stay within the current stack
- no framework / API / language changes
- keep the primary plan to the highest-confidence moves

## Milestone: Modernization

### Task 1: <move title>

**Theme:** Abstraction
**Current state:**
- `src/example.ts:42` — <excerpt or paraphrase>

**Proposed state:** <one paragraph>

**Acceptance:**
- <mechanically verifiable criterion 1>
- <mechanically verifiable criterion 2>

**Estimated blast radius:** <N files>

## Out-of-scope findings (appendix)

## Considered, not in primary plan (appendix)
```

For behaviour-preserving refactors, require characterization tests first.

### 8. Optional handoff

If `--handoff` is set, run:

```text
execute-prd --type=refactor <plan-path>
```

Otherwise stop with the plan path and a concise summary of the top moves.

## Relationship to Copilot built-ins

- Use built-in `/plan` when the user already knows the refactor they want and
  just needs an implementation plan.
- Use this prompt when the missing step is the modernization audit itself:
  deciding which refactors are worth doing now.
- Use built-in `/review` for post-change review, not for generating the
  modernization plan.

## Key Rules

1. Stay within the current stack.
2. Recommend before executing.
3. Keep the move list short and high-confidence.
4. Calibrate to project shape before recommending architecture work.
5. Use representative evidence, not exhaustive evidence.
6. Every accepted move must be mechanically verifiable.

## Do Nots

- Do not edit code directly as part of this prompt.
- Do not turn style-only cleanup into modernization work.
- Do not propose framework, language, or public-API changes in the primary
  plan.
- Do not exhaustive-read a large repo.

## Closed Decisions

- This prompt produces a refactor plan first; execution is a separate step.
- The modernization bar is objective engineering value, not personal taste.
- Within-stack modernization beats speculative redesign.
