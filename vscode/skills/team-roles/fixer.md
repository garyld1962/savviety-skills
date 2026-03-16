# Team Fixer Prompt Template

Open one Copilot chat per branch with Blocker or High review findings (Phase 5, second pass). Only open a fixer chat if the reviewer verdict is FAIL or WARN.

## Placeholders

| Placeholder | Description | Example |
|------------|-------------|---------|
| `<branch-name>` | Branch to fix | `feat/security-hardening` |
| `<worktree-path>` | Absolute path to worktree | `/Users/gary/repos/myproject/.worktrees/security` |
| `<findings>` | Pasted Blocker and High findings from reviewer | (see example below) |
| `<build-cmd>` | Build command | `cd <worktree-path> && pnpm -r build` |
| `<test-cmd>` | Test command | `cd <worktree-path> && pnpm -r test -- --run` |

## Prompt Template

```
Fix the code review findings on branch `<branch-name>` in the worktree at
`<worktree-path>`.

## Findings to Fix

<findings>

## Rules

1. Fix **Blocker** findings first, then **High**.
2. Ignore **Medium**, **Low**, and **Info** findings entirely — do not fix them.
3. Make minimal, targeted changes. Do not refactor surrounding code.
4. If you disagree with a finding, explain why in your report instead of fixing it.

## After Fixing

1. Build: `<build-cmd>`
2. Test: `<test-cmd>`
3. Stage only the files you changed: `git add <file1> <file2> ...`
4. Commit: `git commit -m "fix: address code review findings"`

If build or tests fail after your fixes, debug and fix until they pass.

## Report

For each finding, report one of:
- **Fixed** — What you changed and why
- **Could not fix** — What you tried and what blocked you
- **Disagree** — Why the finding is incorrect or unnecessary
```
