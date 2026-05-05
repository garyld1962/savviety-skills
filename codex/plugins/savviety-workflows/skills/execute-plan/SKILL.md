---
name: execute-plan
description: "Execute a written implementation plan with validation, task checkpoints, reviews, milestone verification, and optional user-authorized parallel lanes."
---

# Execute Plan

Execute a plan end to end, but keep Codex's subagent policy explicit.

Load Codex-native references as needed:

- `references/preflight.md` for validation, branch, toolchain, and safety gates.
- `references/task-loop.md` for sequential task execution, ambiguity handling, decision records, and retries.
- `references/parallel-waves.md` for user-authorized subagent lanes.
- `references/review-gates.md` for milestone and PR-boundary reviews.
- `references/reporting.md` for final reports and postmortems.
- `references/agent-prompts/` for default lane prompt templates.
- `scripts/toolchain_probe.py` for deterministic PATH checks.

`references/legacy/` is archival only. Do not load it during normal execution.

## Workflow

1. Run `validate-plan`.
2. Summarize tasks, milestones, ownership, and verification commands.
3. Ask before using subagents for parallel lanes. If not authorized, execute sequentially.
4. For authorized lanes, use disjoint write scopes and include the multi-agent coordination warning.
5. Run focused verification after each task and full verification at milestones.
6. Run review gates at milestones and the PR boundary.
7. Keep a concise execution log and final report.

Never assume worker agents inherit parent environment or durable state.
