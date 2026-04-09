---
description: >-
  Run a governed postmortem over a completed execution run by inspecting the run
  artifacts, prompt and skill usage, tool usage, and the fit of `AERS.md`, then
  write a structured `postmortem.md`.
argument-hint: "[@run folder or requirements artifact, defaults to latest docs/runs folder when clear]"
agent: "agent"
tools:
  - read
  - search
  - edit
  - codebase
---

# Postmortem

Use this prompt as the human entry point for a run postmortem.

Follow these assets:

- `.github/skills/copilot-platform-playbook/SKILL.md`
- `.github/skills/review-disposition-governance/SKILL.md`
- `.github/docs/process/postmortem-workflow.md`
- `.github/docs/process/evidence-and-artifacts.md`
- `.github/docs/process/document-schema.md`
- `.github/docs/templates/postmortem.template.md`

## Workflow contract

1. Identify the completed run folder under `docs/runs/<yyyy-mm-dd-HHMMSS>/`, or use the folder the user supplied.
2. Review the artifacts relevant to that run, including when present:
   - `execution-report.md`
   - `review-plan.md`
   - `review-code.md`
   - `adversarial-review.md`
   - `disposition-log.md`
3. Use `AERS.md` only as the requirements source of truth; do not rewrite it.
4. Focus on workflow, governance, review quality, tool usage, and process weaknesses.
5. Write the result using the canonical template to `postmortem.md` in the run folder.

## Output goals

The postmortem should make it easy for a senior developer to understand:

- what happened
- what worked
- what broke down
- what the process missed
- what should change next

## CRITICAL: Do Not Guess

- Do NOT turn the postmortem into a second requirements document.
- Do NOT simply summarize the whole chat transcript.
- Do NOT restate review findings without explaining their process significance.
- Do NOT write outside the canonical run artifact structure without a clear reason.
