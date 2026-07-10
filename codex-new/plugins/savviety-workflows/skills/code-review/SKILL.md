---
name: code-review
description: "Domain-aware code review controller. Triage a diff, select review lenses, and report line-cited findings for correctness, security, tests, architecture, performance, and operability."
---

# Code Review

Review code in a findings-first style.

Load Codex-native references as needed:

- `references/controller/codex-controller.md` for controller workflow.
- `references/profiles/` for `breakpoint` and `full` review profiles.
- `references/concept/` for domain lenses and severity.
- `references/dialect/` for language overlays.
- `references/platform/` for platform overlays.
- `scripts/diff_triage.py` for a first-pass changed-file manifest.

`references/legacy/` is archival only. Do not load it during normal review.

## Workflow

1. Identify the diff or review target.
2. Select the minimum relevant lenses from `references/concept/`, `references/dialect/`, `references/platform/`, and `references/profiles/`.
3. Review locally unless the user explicitly asks for subagents. If authorized, use `review_worker` or `review_explorer`.
4. Lead with findings ordered by severity and cite files/lines.
5. Include open questions and test gaps after findings.

Do not produce style-only noise. Every finding needs a concrete behavioral, security, maintainability, or verification risk.
