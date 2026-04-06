# Team Reviewer Prompt Template

Open one Copilot chat per branch in Phase 5 (first pass). All reviewers should open their chats in parallel.

## Placeholders

| Placeholder | Description | Example |
|------------|-------------|---------|
| `<branch-name>` | Branch to review | `feat/security-hardening` |
| `<worktree-path>` | Absolute path to worktree | `/Users/gary/repos/myproject/.worktrees/security` |
| `<plan-path>` | Absolute path to implementation plan | `/Users/gary/repos/myproject/docs/plans/2026-02-17-wave1-implementation.md` |
| `<team-section>` | Team name/section in the plan | `Team 1: Security Hardening` |
| `<build-cmd>` | Build command | `cd <worktree-path> && pnpm -r build` |
| `<test-cmd>` | Test command | `cd <worktree-path> && pnpm -r test -- --run` |

## Prompt Template

```
Review the code on branch `<branch-name>` in the worktree at `<worktree-path>`.

Compare against the plan at `<plan-path>`, section: <team-section>.

## Review Process

### Step 1: Code Quality Review

Examine the changed files in the worktree for:
- **TypeScript quality** — types, error handling, logging
- **API patterns** — validation, messaging contracts, shutdown logic
- **Test quality** — coverage, isolation, determinism
- **Security** — injection vulnerabilities, auth checks, data exposure risks

### Step 2: Plan Alignment (manual check)

Verify:
1. **Completeness** — Are all tasks in <team-section> implemented?
2. **Accuracy** — Does the implementation match the plan?
3. **Scope** — Is there extra work beyond the plan?

### Step 3: Build & Test

1. Build: `<build-cmd>`
2. Test: `<test-cmd>`

## Severity Classification

| Severity | Criteria | Action |
|----------|----------|--------|
| **Blocker** | Data loss risk, security vulnerability, crash on happy path | Must fix before merge |
| **High** | Missing validation, test cleanup leak, type mismatch | Should fix |
| **Medium** | Accessibility, debouncing, additional test coverage | Defer to future work |
| **Low** | Style nits, naming preferences | Optional |
| **Info** | Observations, suggestions | No action needed |

## Verdict

- **PASS**: No Blocker or High findings
- **WARN**: Has High findings but no Blockers
- **FAIL**: Has Blocker findings (must fix before merge)
```
