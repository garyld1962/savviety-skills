---
name: execute-plan
description: "Execute an existing written implementation plan end-to-end with validation, task checkpoints, focused build/test cycles, milestone verification, review gates, retry discipline, and optional user-authorized parallel lanes. Use when the user already has a plan file, often produced by execute-prd, and says 'execute the plan', 'run docs/plans/X.md', 'resume the plan', or 'work through this plan'. Prefer this over ad-hoc execution when the plan has tasks, acceptance criteria, verification commands, or parallel metadata."
---

# Execute Plan

Execute a plan end to end, but keep Codex's subagent policy explicit.

Load Codex-native references as needed:

- `references/preflight.md` for validation, branch, toolchain, and safety gates.
- `references/task-loop.md` for sequential task execution, ambiguity handling, decision records, and retries.
- `references/parallel-waves.md` for user-authorized subagent lanes.
- `references/review-gates.md` for milestone and PR-boundary reviews.
- `references/loop-fuse.md` for stopping repeated verification/tool loops.
- `references/reporting.md` for final reports and postmortems.
- `references/agent-prompts/` for default lane prompt templates.
- `scripts/toolchain_probe.py` for deterministic PATH checks.

`references/legacy/` is archival only. Do not load it during normal execution.

## Relationship To Codex Behavior

This skill is the structured plan executor for Savviety workflows. It adds plan validation, delivery contracts, per-task verification, review gates, and explicit subagent authorization around normal Codex implementation work. For vague intent without a plan, use `execute-prd` or clarify requirements first. For a trivial change, edit directly.

## Workflow

1. Run `validate-plan`.
2. Summarize tasks, milestones, ownership, and verification commands.
3. Ask before using subagents for parallel lanes. If not authorized, execute sequentially.
4. For authorized lanes, use disjoint write scopes and include the multi-agent coordination warning.
5. Run focused verification after each task and full verification at milestones.
6. Apply the loop fuse before every verification rerun or alternate probe.
7. Run review gates at milestones and the PR boundary.
8. Keep a concise execution log and final report.

Never assume worker agents inherit parent environment or durable state.
