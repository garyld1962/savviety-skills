---
description: >-
  Reads accumulated postmortems, groups taxonomy-tagged recommendations, and
  proposes edits to prompts, skills, or plan templates to improve the
  development workflow. Use after running several postmortems. Do not use
  without postmortem data — it needs real run history of at least 3–5 runs
  before recommendations are meaningful signal rather than one-off noise.
argument-hint: "[path/to/postmortem-index.json, default: docs/postmortems/index.json]"
agent: agent
tools:
  - read
  - search
  - edit
  - codebase
---

# Process Tuning

Consume the postmortem index, surface recurring recommendations, and propose
concrete artefact edits. This is the *write* side of the auto-improve loop that
`postmortem` and `execute-plan` Phase 5 feed.

**Proposal-only by default.** Write a tuning report listing edits and the
evidence behind them. Do not apply changes directly. The operator (or a
follow-on `execute-plan` run) makes the actual changes.

## When to use

- At least 5 postmortems have landed in `docs/postmortems/index.json` and you
  want to act on the patterns.
- You suspect a specific gate, rubric, or closed-decision area is drifting and
  want the index queried for evidence.
- Periodically (monthly, quarterly) as part of a process-health review.

## When NOT to use

- Fewer than ~3–5 postmortems exist for the recommendations being considered.
  A single postmortem flagging an issue is not signal — it may be a one-off
  run pathology. Wait for recurrence.
- You want to analyse a single run — use `postmortem` instead.
- You want to apply edits the proposal already names — that's `execute-plan`
  work; feed it a plan that wraps the edits.

## Arguments

| Argument | Description |
|---|---|
| `--index=<path>` | Path to the postmortem index. Default: `docs/postmortems/index.json`. |
| `--min-runs=<N>` | Minimum distinct runs a recommendation must appear across before it is surfaced. Default: `3`. |
| `--since=<date>` | Only consider postmortems on or after this ISO date. Default: all rows. |
| `--target=<value>` | Filter to one taxonomy `target` (e.g. `adversarial-triggers`). Repeatable. Default: all. |
| `--type=<value>` | Filter to one taxonomy `type` (e.g. `tune-threshold`). Repeatable. Default: all. |
| `--report-path=<path>` | Where to write the tuning report. Default: `docs/postmortems/tuning-<YYYYMMDD-HHMMSS>.md`. |
| `--apply` | Off by default. When set, generate a plan artefact at `docs/plans/process-tune-<slug>.md` capturing each high-confidence proposal as a task. Does NOT execute it; that is still the operator's call. |

## Workflow

### 1. Load the index

Read `docs/postmortems/index.json` (or `--index=<path>`). If it does not exist
or is empty, halt:

```
No postmortems to tune from. The postmortem prompt hasn't run yet, or the
index is at a different path.
```

Apply the `--since`, `--target`, and `--type` filters before grouping.

### 2. Group recommendations

Group every recommendation row across the filtered runs by the composite key
`(target, type)`. Within each group, count distinct runs (deduplicate by the
`run` field — repeated postmortems on the same run still count once) and
aggregate the evidence.

Discard groups with fewer than `--min-runs` distinct runs.

### 3. Score each group

For each surviving group, compute:

- **frequency** — number of distinct runs flagging this `(target, type)` pair.
- **mean confidence** — average of the `confidence` values (`high=3`,
  `medium=2`, `low=1`).
- **actionability ratio** — fraction of recommendations in the group with
  `actionable: true`.
- **recency** — number of runs in the most recent 5 that flagged it.

These are internal scoring inputs. Rank groups in the report by
**frequency × mean-confidence × actionability-ratio**, with recency as the
tiebreaker.

### 4. Emit a tuning report

Write the markdown report at `--report-path`. Structure:

```
# Process Tuning Report

## Summary
- **Index:** docs/postmortems/index.json
- **Window:** <since>..<latest>  (<N> runs)
- **Filters:** target=<...> type=<...>
- **Surfaced groups:** <K>

## Recommendations

### Group 1: <target> / <type>  (<frequency> runs)

**Pattern:** <one sentence summarising the recurring complaint>

**Evidence:**
| Run | Recommendation summary | Confidence |
|---|---|---|
| 2026-04-12-091200 | ... | high |
| 2026-04-19-141500 | ... | high |
| 2026-05-02-082000 | ... | medium |

**Proposed edit:**
<Concrete change, naming the file and the operation. Examples:
- "Lower `adversarial_triggers` threshold from 200 → 150 lines in the
  repo's copilot-instructions.md ## Commands section."
- "Add a closed decision at
  `closed-decisions/auth/session-cookie-name.md` with the value the
  last three plans re-debated."
- "Tighten the domain-review prompt `breakpoint` section to also run the
  `tests-cover-changed-paths` check.">

**Risk of acting:** <one line — what could go wrong if applied>

**Confidence to act:** high | medium | low
```

Group order: highest score first.

### 5. Optional: emit an actionable plan

When `--apply` is set, also write a plan-shaped file at
`docs/plans/process-tune-<YYYYMMDD-HHMMSS>.md` containing one task per
`confidence: high` group. Each task names the file to edit, the operation, and
an acceptance bullet that is mechanically verifiable (a search pattern, a
numeric value, a closed-decision file exists). The plan does NOT auto-execute
— the operator chooses whether to feed it to `execute-plan`.

This split (proposal-only vs. plan emission) is deliberate. Process edits land
in the same artefacts that govern future runs; an auto-applied edit changes the
rules of engagement without an auditable approval. The plan path keeps the
human in the loop while removing the busy-work of authoring tasks from a known
list of groups.

### 6. Report

After writing files, output:

```
Tuning report: <report-path>
Surfaced groups: <K>  (<H> high-confidence, <M> medium, <L> low)
[--apply]  Plan emitted: <plan-path>  Run execute-plan to apply.
```

## Hard rules

- **Read-only by default.** Write a report and (when `--apply` is set) a plan
  file. Do NOT edit `_internal/`, `closed-decisions/`, `copilot-instructions.md`,
  or any other governing artefact directly.
- **Frequency is the primary filter.** A single postmortem flagging an issue is
  below threshold, even if its `confidence` is `high`. Drift fixes that overfit
  to one run are themselves drift.
- **Recommendations the index cannot ground go in a separate section.** If a
  group has `target: other`, surface it in a tail section labelled
  "**Recommendations needing taxonomy extension**" so the taxonomy itself can
  be improved. Do not silently drop them.
- **The taxonomy is owned by execute-plan Phase 5.** If process-tune keeps
  proposing taxonomy changes, the change goes into the `execute-plan` skill or
  prompt → Phase 5 → "Recommendation taxonomy", not into a parallel definition
  here.

## CRITICAL: Do Not Guess

- Do not synthesise recommendations the index does not contain. Every surfaced
  group must trace back to ≥`--min-runs` distinct postmortems.
- Do not edit governing artefacts directly, even when `--apply` is set.
  `--apply` produces a plan; the plan goes through `execute-plan` like any
  other change. Process edits get the same scrutiny as feature edits.
- Do not delete or rewrite rows in `docs/postmortems/index.json`. The index is
  append-only. Outdated recommendations stay as evidence; the scoring logic
  naturally weights recency.
- Do not run on an empty or near-empty index. The `--min-runs=3` default exists
  to prevent overfitting; lowering it is a smell.
