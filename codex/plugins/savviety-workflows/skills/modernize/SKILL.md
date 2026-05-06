---
name: modernize
description: "Audit an older or dormant codebase against current Codex/agent capability and produce a prescriptive within-stack refactor plan. Use for phrases like 'modernize this codebase', 'refresh the code', 'what would this look like today', 'AI-time refresh', or 'modernization audit'. Focuses on structure, boundaries, types, error handling, tests, infra organization, and dead code. Does not recommend framework changes, language switches, public API rewrites, dependency-upgrade campaigns, or broad redesigns."
---

# Modernize

Read an existing codebase holistically and produce a short, execution-ready refactor plan calibrated to what current Codex workflows can safely carry out. This is a planning front end for `execute-prd --type=refactor`, not a free-form audit report and not an automatic rewrite.

Load `references/modernization-rubric.md` before making findings.

## When To Use

- A project has been dormant for months or was last worked on with weaker agent tooling.
- The code has older-agent patterns: excessive defensive branching, weak typing, kitchen-sink utilities, mixed concerns, or shallow tests.
- The user asks to modernize, refresh, revisit, or ask what the code would look like with today's tooling.
- The desired output is a refactor plan that can be reviewed or handed to `execute-prd`.

## When Not To Use

- The user has a specific bug or feature request. Handle that request directly or use `execute-prd`.
- The project likely needs a new framework, language, database, or public API shape. Surface that as an out-of-scope note only.
- The task is dependency-driven modernization, CVEs, lockfile churn, or package upgrade work. Use `dep-audit` and `dep-migrate`.
- The repo is tiny, roughly under 500 LOC. Recommend direct edits or a focused simplification instead.
- The user wants broad ecosystem or installed-skill review. Use `skills --audit`.

## Arguments

- `[path]`: codebase root. Default: current working directory.
- `--report-only`: write the modernization plan and stop.
- `--handoff`: after writing the plan, run `execute-prd --type=refactor <plan-path>`. Use only when the user clearly asked for execution.
- `--out=<path>`: output path. Default: `docs/plans/modernization-<YYYYMMDD>.md`.
- `--max-moves=<N>`: cap primary plan moves. Default: 10.
- `--theme=<name>`: restrict to one or more themes: `abstraction`, `separation`, `types`, `errors`, `tests`, `infra`.

## Workflow

1. Detect project shape: language, project type, size class, test coverage signal, and visible architecture pattern.
2. Halt on tiny repos and very large repos where a per-package audit is safer.
3. Run `audit-existing` for descriptive state. Carry its evidence forward; do not duplicate the whole audit.
4. Sample-read by the rubric: breadth, depth, boundaries, public surface, hotspots, and test parity. Do not exhaustive-read large repos.
5. Classify findings by theme and decide whether current agent capability materially lowers the risk of fixing them now.
6. Cull aggressively with the rubric's senior-engineer, taste-call, within-stack, blast-radius, and cap tests.
7. Write a plan shaped for `execute-prd --type=refactor`, with mechanically verifiable acceptance criteria and characterization tests before behavior-preserving changes.
8. If `--handoff` is explicit, invoke `execute-prd --type=refactor <plan-path>` after the plan exists. Otherwise stop with the plan path.

## Output Shape

The plan should include:

- Frontmatter: `slug`, `source_prd`, `intent: refactor`, `type: refactor`.
- Summary table by theme.
- Closed decisions: stay within current stack, no framework/API/language changes, blast-radius ceiling.
- One milestone containing the selected modernization tasks.
- For each task: theme, representative `file:line` evidence, proposed state, acceptance criteria, and estimated blast radius.
- Appendix for out-of-scope findings and considered-but-not-primary moves.

## Key Rules

1. Stay within the current stack. Framework, language, database, and public-API changes belong in the appendix.
2. Recommend before executing. Do not edit code directly as part of this skill.
3. Prefer a short list of high-confidence moves over a comprehensive catalog of taste calls.
4. Calibrate to project shape. A 700-line CLI does not need a service architecture.
5. Use representative evidence. Three examples per move is enough.
6. Make each accepted move verifiable. Refactor tasks need characterization tests first when behavior could change.
