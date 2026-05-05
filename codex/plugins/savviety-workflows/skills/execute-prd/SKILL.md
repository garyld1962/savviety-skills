---
name: execute-prd
description: "Convert a PRD, story, work item, or rough requirement into an executable plan, validate it, optimize parallel lanes, then execute when approved."
---

# Execute PRD

This is the Codex consolidation point for Claude `execute-prd` and lightweight `kickoff` behavior.

Read `references/workflow.md` for full PRD-to-plan behavior and `references/kickoff.md` for lightweight kickoff. `references/legacy/` and `references/legacy-kickoff/` are archival only.

## Workflow

1. Load the requirement source from a file, direct prompt, or work item.
2. Run readiness checks with `prd-validate` when ambiguity blocks execution.
3. Draft an implementation plan with acceptance criteria.
4. Run `parallel-optimization` only when concurrency looks useful.
5. Run `validate-plan`.
6. Execute only after the user confirms the plan or has clearly requested autonomous execution.
