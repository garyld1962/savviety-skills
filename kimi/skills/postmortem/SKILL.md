---
name: postmortem
description: Structured retrospective over a completed execute-plan run. Reads the
  run folder, writes postmortem.md + postmortem.json, and appends to the postmortem
  index.
whenToUse: Structured retrospective over a completed execute-plan run. Reads the run
  folder, writes postmortem.md + postmortem.json, and appends to the postmortem index.
---


# /skill:postmortem — Retroactive Retrospective for an `/skill:execute-plan` Run

**Purpose:** produce the same postmortem `/skill:execute-plan`
auto-fires, but on demand against a previously-completed run folder.
Every recommendation is tagged with the postmortem taxonomy so it
aggregates across runs and feeds `/skill:process-tune`.

This skill is the read-only counterpart of execute-plan's postmortem
step. The implementation, schemas, taxonomy, and hard rules live in
the `## Postmortem` section of `claude/execute-plan/SKILL.md`. This
skill defers to that section — do not duplicate the rules here.

## When to Use

- A past `/skill:execute-plan` run completed without firing the postmortem
  (clean `PASS`) and you want to learn from it anyway.
- You want to re-run the postmortem after editing the run's artefacts
  (e.g. you added evidence to a finding, or the source PRD was
  updated and you want the requirements-fit lens re-applied).
- You're analysing a run produced by an older `/skill:execute-plan` that
  pre-dates the structured-recommendation taxonomy and want to
  back-fill the index.

## When NOT to Use

- The run hasn't completed yet — `/skill:execute-plan`'s postmortem step
  will fire if the trigger rules match. Don't pre-empt it.
- You want to re-review code quality — use `/skill:domain-review` or
  `/skill:review-adversarial`.
- Production-incident retrospective — this skill is for
  workflow runs, not outages. Use a different format (e.g. five-whys)
  for production incidents.

## Arguments

| Argument | Description |
|---|---|
| `<run-folder>` | Path to the completed run folder (e.g. `docs/runs/2026-04-06-143000/`). If omitted, picks the most recent folder under `runs_root` from the repo-delivery `## Commands` schema. |
| `--mode=<auto\|full\|lightweight>` | Depth of the postmortem. Default `auto`. Resolves the same way as `/skill:execute-plan --postmortem-mode`: `lightweight` for `PASS`-with-soft-triggers, `full` otherwise. |
| `--reason=<string>` | One-line note recorded in the JSON `trigger` field. Useful when invoking on a clean `PASS` to capture *why* you wanted a postmortem ("validating new aers-readiness rule"). |
| `--no-index` | Skip appending to `docs/postmortems/index.json`. Default is to append; only set this for exploratory runs you don't want in the long-term aggregate. |

## Workflow

### 1. Locate the run folder

If `<run-folder>` is supplied, use it. Otherwise read `runs_root:`
from the repo's `CLAUDE.md ## Commands` schema and pick the most
recent timestamped subfolder.

If neither path exists, halt:

```
No run folder found.
Pass an explicit path: /skill:postmortem docs/runs/<yyyy-mm-dd-HHMMSS>/
```

### 2. Verify required inputs

The run folder must contain at minimum `execution-report.json`. If
absent, halt — there is no structured run to analyse.

Read every artefact present:

- `execution-report.md` and `.json` (required)
- `disposition-log.md` (optional)
- the plan file referenced by `execution-report.json#plan_file`
- the source PRD/AERS, if discoverable from the plan's frontmatter
  (`source_prd:`)

### 3. Apply the postmortem logic

Run the postmortem analysis exactly as defined in the `## Postmortem`
section of `claude/execute-plan/SKILL.md`. That section
is the single source of truth for:

- mode resolution
- markdown structure (full and lightweight)
- the two named lenses (`Tool and skill usage`, `Requirements fit`)
- the recommendation taxonomy (`target` and `type` vocabularies)
- the JSON schema for `postmortem.json`
- the hard rules
- the headline-recommendation rule

The only difference between the auto-fired postmortem and this skill
(invoked on demand):

- **Trigger source.** The auto-fired postmortem runs automatically
  based on the run's verdict and gate state. This skill fires because
  the operator asked. Record the operator's `--reason` (or
  `"manual: <run-folder>"` when none was given) in the JSON `trigger`
  field.
- **Output location.** The auto-fired postmortem writes adjacent to
  the execution report. This skill writes into the same folder. If a previous
  `postmortem.md`/`.json` already exists, write to
  `postmortem-<YYYYMMDDHHMMSS>.md`/`.json` instead — never
  overwrite. The index gets one row per file.

### 4. Append to the index

Unless `--no-index` is set, append a row to
`docs/postmortems/index.json` per the schema in the `### Cross-run
aggregation` subsection of `claude/execute-plan/SKILL.md`'s
`## Postmortem` section. Create the file as `[]` if it does
not exist.

### 5. Report

```
Postmortem: <path-to-postmortem.md>  (mode: <mode>)
Key recommendation: <postmortem.headline>
Index: appended to docs/postmortems/index.json (run <run-id>)
```

If `--no-index` was passed:

```
Postmortem: <path-to-postmortem.md>  (mode: <mode>)
Key recommendation: <postmortem.headline>
Index: skipped (--no-index)
```

## Hard rules

All hard rules from the `## Postmortem` section of
`claude/execute-plan/SKILL.md` apply unchanged:

- not a second requirements document
- not a chat-transcript summary
- not a restatement of review findings
- not a blame document
- length cap: one page (full) / half page (lightweight)
- recommendations must use the taxonomy

Plus one additional rule specific to this skill:

- **Never overwrite a prior postmortem.** Use a timestamped suffix on
  re-runs. The index relies on every postmortem being a stable,
  immutable artefact — overwriting one rewrites history.

## Things you must not do

- Do not invent a different schema or taxonomy. The taxonomy is
  centralised in the `## Postmortem` section of
  `claude/execute-plan/SKILL.md` so that `/skill:process-tune` can
  group recommendations across runs.
- Do not skip the index append unless `--no-index` is explicit. Silent
  index skips defeat the auto-improve loop this skill exists to feed.
- Do not modify run artefacts other than writing
  `postmortem*.md` / `postmortem*.json` and appending to the index.
