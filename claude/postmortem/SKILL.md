---
name: postmortem
description: "Run a structured retrospective over a completed governed execution run. Analyzes workflow, review quality, tool usage, and process gaps. Writes postmortem.md in the run folder."
model: opus
---

# /postmortem — Governed Run Retrospective

**Purpose:** Analyze a completed governed execution run and produce a structured postmortem. Focuses on process effectiveness — what the workflow caught, what it missed, and what should change — not on re-reviewing the code.

## When to Use

- A `/execute-workflow` run has completed (PR merged or rejected)
- You want to evaluate the workflow itself — gates, reviews, tool usage
- Recurring issues suggest the process needs tuning

## When NOT to Use

- Re-reviewing code quality — use `/code-review` or `/review-adversarial`
- No governed run artifacts exist — postmortem needs the run folder
- Incident retrospective for production issues — this skill is for workflow runs, not outages

## Pre-flight Required Config

This skill shares config with `/execute-workflow`.

1. Check `<project>/.claude/workflow.config.md` exists and has `process_docs_root`, `templates_root`, and `runs_root` populated.
   If not: "Run `/configure workflow` to set up workflow config."

2. Verify the postmortem template exists at `templates_root/postmortem.template.md`.
   If not: "Copy the reference template from `claude/execute-workflow/artifact-templates.template/postmortem.template.md`."

3. If healthy, proceed silently.

## Arguments

- `<run-folder>` — path to the completed run folder (e.g., `docs/runs/2026-04-06-143000/`). If not provided, use the most recent folder under `runs_root`.
- `--lightweight` — produce a shorter postmortem (skip detailed tool/skill analysis)

## Rubrics

This skill references:
- `_rubrics/disposition` — governance rules, status vocabulary
- Process doc: `postmortem-workflow.md` from the project's `process_docs_root`

## Workflow

### Step 1: Identify the Run

Find or accept the run folder. Verify it contains at least `execution-report.md`.

If no run folder is found or specified, halt:
> No run folder found. Provide a path: `/postmortem docs/runs/yyyy-mm-dd-HHMMSS/`

### Step 2: Read Run Artifacts

Read the artifacts present in the run folder:
- `execution-report.md` (required)
- `review-code.md` (if present)
- `adversarial-review.md` (if present)
- `disposition-log.md` (if present)
- `review-plan.md` (if present)

Also read the original requirements artifact referenced in the execution report.

### Step 3: Analyze

Focus on these areas (per project's `postmortem-workflow.md`):

1. **Workflow execution** — Did each phase add value? Were phases skipped or rushed?
2. **Review quality** — Were findings evidence-based? Coverage gaps?
3. **Disposition effectiveness** — Did the loop converge? Were escalations justified?
4. **Tool and skill usage** — Right tools for the job? Gaps or misuse?
5. **Requirements fit** — Was the AERS/PRD clear enough? Did ambiguity cause rework?
6. **Process gaps** — What did the process NOT catch?

For `--lightweight`, cover only items 1, 3, and 6.

### Step 4: Write Postmortem

Write `postmortem.md` in the run folder using the project's postmortem template.

The postmortem should make it easy for a senior developer to understand:
- what happened
- what worked
- what broke down
- what the process missed
- what should change next

### Step 5: Report

> "Postmortem written to `<run-folder>/postmortem.md`."
> "Key finding: <one-line summary of the most actionable recommendation>"

## CRITICAL: Do Not Guess

- Do NOT turn the postmortem into a second requirements document.
- Do NOT simply summarize the conversation transcript.
- Do NOT restate review findings without explaining their process significance.
- Do NOT write outside the run folder without a clear reason.
- Do NOT skip reading the actual run artifacts — they are the evidence.
