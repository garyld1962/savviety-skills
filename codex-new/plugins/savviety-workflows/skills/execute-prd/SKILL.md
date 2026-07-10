---
name: execute-prd
description: "Convert a PRD, RFC, prompt, story, work item, or rough requirement into an executable plan, validate it, optimize safe parallel lanes, then execute when approved. Use for phrases like 'build this PRD', 'execute the PRD', 'turn this RFC into a plan and run it', 'implement prompt.md', 'turn these requirements into an app', 'kickoff this feature', or 'start this story'. Prefer this over generic planning when a concrete requirement source exists and the user wants implementation, not just brainstorming."
---

# Execute PRD

This skill consolidates the full PRD execution path with lightweight kickoff behavior.

Read `references/workflow.md` for full PRD-to-plan behavior and `references/kickoff.md` for lightweight kickoff. `references/legacy/` and `references/legacy-kickoff/` are archival only.

## Relationship To Codex Behavior

This skill is the structured PRD-to-execution path for Savviety workflows. Use it when the input is a concrete requirement source and the output should be a validated plan, optionally followed by implementation. For a small direct edit, make the edit directly. For an already-written plan, use `execute-plan`.

## Workflow

1. Load the requirement source from a file, direct prompt, or work item.
2. Run readiness checks with `prd-validate` when ambiguity blocks execution.
3. Draft an implementation plan with acceptance criteria.
4. Run `parallel-optimization` only when concurrency looks useful.
5. Run `validate-plan`.
6. When executing, apply `execute-plan` including its loop fuse; repeated verification failures must stop with a blocker report.
7. Execute only after the user confirms the plan or has clearly requested autonomous execution.
