---
name: prd-acceptance
description: "Verify delivered work against PRD or AERS acceptance criteria. Produces a criterion-by-criterion evidence scorecard."
---

# PRD Acceptance

Read `references/workflow.md` and `references/aers-readiness.md`. `references/legacy/` is archival only.

## Workflow

1. Extract acceptance criteria from the PRD or AERS.
2. Map each criterion to code, tests, UI/API behavior, or documentation evidence.
3. Run verification commands where safe.
4. Mark each item pass, fail, partial, or unverifiable.
5. Report gaps before recommending ship.
