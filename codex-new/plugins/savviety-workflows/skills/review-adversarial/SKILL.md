---
name: review-adversarial
description: "High-stakes adversarial code review after normal review. Challenges assumptions with distinct reviewer lenses and optional configured external model/CLI reviewers."
---

# Review Adversarial

Use for auth, payments, migrations, security-sensitive diffs, or large changes.

Load Codex-native references as needed:

- `references/workflow.md` for trigger, model, lens, and synthesis rules.
- `references/reviewer-lenses.md` for reviewer perspectives.
- `scripts/cli_probe.py` to check available external reviewer CLIs.

`references/legacy/` is archival only. Do not load it during normal review.

Prefer a different external model or CLI. If subagents are authorized as a fallback, clearly label the result as same-model adversarial review. Otherwise run lenses sequentially and clearly label each perspective.
