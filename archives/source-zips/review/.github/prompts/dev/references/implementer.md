# Team Implementer Prompt Template

Open one Copilot chat per team in Phase 4. All teams should open their Copilot chats in parallel (start all conversations at roughly the same time).

## Placeholders

| Placeholder | Description | Example |
|------------|-------------|---------|
| `<team-name>` | Human-readable team name | `Security Hardening` |
| `<worktree-path>` | Absolute path to worktree | `/Users/gary/repos/myproject/.worktrees/security` |
| `<branch-name>` | Git branch name | `feat/security-hardening` |
| `<plan-path>` | Absolute path to implementation plan | `/Users/gary/repos/myproject/docs/plans/2026-02-17-wave1-implementation.md` |
| `<task-range>` | Task numbers to implement | `Tasks 1-7` |
| `<build-cmd>` | Build command for verification | `cd <worktree-path> && pnpm -r build` |
| `<test-cmd>` | Test command for final verification | `cd <worktree-path> && pnpm -r test -- --run` |

## Prompt Template

```
You are Team: <team-name>.

Implement <task-range> from the implementation plan in the worktree at
`<worktree-path>`.

Branch: `<branch-name>`
Plan: `<plan-path>`

## Instructions

1. Read the plan file first. Find your team's section and understand all tasks before starting.
2. Implement each task in order, following each step exactly as written.
3. After each task:
   - Build: `<build-cmd>`
   - If the build fails, fix the error before moving to the next task.
   - Commit with the message specified in the plan.
4. After completing all tasks:
   - Run the full test suite: `<test-cmd>`
   - If tests fail, fix failures and commit the fixes.

## Rules

- Follow each step exactly as written in the plan. Do not improvise or take shortcuts.
- Do NOT modify files outside your worktree at `<worktree-path>`.
- Use absolute paths for all file operations.
- If the plan specifies code, use that code. Do not rewrite it in your own style.
- If a step is ambiguous, implement the most straightforward interpretation.

## Report

When complete, report:

1. **Tasks completed:** List each task with its commit SHA
2. **Build status:** Pass/fail (with error if fail)
3. **Test status:** Pass/fail (N tests passing, M failing)
4. **Files changed:** List of files created or modified
5. **Deviations:** Any differences from the plan and why
```
