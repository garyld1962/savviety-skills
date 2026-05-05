# Codex Code Review Controller

Use this guide instead of the archived legacy controller.

## Inputs

- Review target: git diff, PR, branch range, file list, or user-provided patch.
- Optional profile: `breakpoint` or `full`. Default to `full`.
- Optional diff manifest from `execute-plan`.
- Optional intent or PR description.

## Workflow

1. Identify the target diff and enough surrounding context to make line-cited findings.
2. Load `references/profiles/<profile>.yaml`.
3. If a diff manifest is not supplied, run local triage. `scripts/diff_triage.py` can produce a first-pass manifest from changed paths.
4. Select concept domains from `references/concept/`.
5. Select overlays from `references/dialect/` and `references/platform/` only when their parent concept domain is selected.
6. Review locally unless the user explicitly asked for subagents. If subagents are authorized, each worker gets one domain, selected overlays, changed files, and immediate context only.
7. Merge findings by severity and preserve precise file and line references.

## Output

Lead with findings. Use this order:

1. Critical
2. Major
3. Minor
4. Nits
5. Questions
6. Verdict

Omit empty severity sections.

## Guardrails

- Do not produce style-only noise.
- Do not run domains outside the selected profile.
- Do not bury findings behind summaries.
- Do not claim a finding without a concrete failure mode, maintainability risk, security risk, or missing verification.

