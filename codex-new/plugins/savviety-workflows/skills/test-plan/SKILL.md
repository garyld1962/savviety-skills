---
name: test-plan
description: "Create or refresh a TDD-first test plan from requirements. Produces test specifications, priority, analysts, and optional test stubs."
---

# Test Plan

Load Codex-native references as needed:

- `references/orchestrator.md` for modes, discovery, analyst selection, consolidation, and output.
- `references/analysts/` for analyst-specific test specification lenses.
- `references/foundations/` for schemas, priority rubric, project config, reports, and team protocol.
- `references/test-writer.md` for generated test stub shape.
- `references/dependency-classification.md` for testability classification.
- `scripts/plan_summary.py` for quick summaries of existing `.test-plan/plan-latest.json` files.

`references/legacy/` is archival only. Do not load it during normal planning.

Generate test plans before implementation when behavior is still being shaped. Write test files only when the user asks or the workflow explicitly requires it.
