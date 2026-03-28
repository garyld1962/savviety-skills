---
description: "Split work across parallel teams using git worktrees. Covers team boundaries, worktree setup, parallel build, review, merge, and integration testing."
---

# Parallel Teams

Run 2-4 implementation teams concurrently within a single **Wave** using git worktrees and separate Copilot chat sessions. Each team gets an isolated worktree, implements from a shared plan, gets reviewed, and merges sequentially.

**Core principle:** Worktree isolation + parallel Copilot chat sessions + sequential merge = safe concurrent development within a Wave.

## When to Use

- Work spans multiple packages or services
- Can split into 2-4 independent streams
- Clear file ownership per team (no two teams editing the same files)

If any criterion fails, use sequential single-branch development instead.

## Checklist

1. **Design** — Write team-structured design doc (`docs/plans/YYYY-MM-DD-<topic>-design.md`)
2. **Plan** — Write per-team implementation plan (`docs/plans/YYYY-MM-DD-<topic>-implementation.md`)
3. **Worktrees** — Create worktrees + install deps in each
4. **Parallel Build** — Dispatch build agents (one per team, all in one message)
5. **Review & Fix** — Dispatch review agents, then fix agents for Blocker/High findings
6. **Merge & Deploy** — Sequential merge, integration test, deploy, cleanup

## Phase Reference

| Phase | Action | Output | Details |
|-------|--------|--------|---------|
| 1. Design | Divide work into teams | `docs/plans/*-design.md` | Team boundary exploration |
| 2. Plan | Convert design into tasks | `docs/plans/*-implementation.md` | Detailed implementation plan |
| 3. Worktrees | `git worktree add .worktrees/<slug> -b feat/<name> main` + install | Worktrees ready | Git worktree setup |
| 4. Build | Open separate Copilot chat per team | Commits on each branch | Use [implementer](./references/implementer.md) template |
| 5. Review | Open separate Copilot chat per branch | Review findings + fixes | Use [reviewer](./references/reviewer.md) then [fixer](./references/fixer.md) template |
| 6. Merge | Push, PR, merge sequentially; integration test | PRs merged | Git merge workflow |

## Team Boundary Guidelines

| Good Split | Why |
|-----------|-----|
| Backend API vs. UI pages | Different packages, different file trees |
| New service vs. infrastructure | New files vs. config changes |
| Test suite vs. feature code | Test files rarely conflict with source |

| Bad Split | Why |
|----------|-----|
| Two teams editing the same file | Guaranteed merge conflicts |
| Shared types team + consumer team | Consumer blocks on types being done |

When overlap is unavoidable, merge the types provider first and rebase the consumer.

## Merge Order

1. Dependency provider merges first (shared types before consumers)
2. Infrastructure before dependents
3. If no dependencies, smallest diff first
4. Always run integration test on main after each merge

```bash
# Pattern: merge team-one first
cd .worktrees/team-one && git push -u origin feat/team-one
gh pr create --title "feat: Team One" --body "..."
gh pr merge <number> --squash

# Pull merged main
cd /project/root && git pull origin main

# Rebase team-two on updated main
cd .worktrees/team-two && git fetch origin main && git rebase origin/main
git push -u origin feat/team-two --force-with-lease
gh pr create --title "feat: Team Two" --body "..."
gh pr merge <number> --squash

# Integration test
cd /project/root && git pull origin main
pnpm install && pnpm -r build && pnpm -r test
```

## Red Flags

**Never:**
- More than 4 teams per Wave
- Skip code review
- Use relative paths in Copilot prompts
- Skip `pnpm install` in worktrees
- Dispatch build agents sequentially (dispatch all in one message)
- Skip integration test after merging all branches

**Always:**
- Use absolute paths in all Copilot prompts
- Build after every task within a team
- Commit after every task within a team
- Run integration test on main after all merges complete
- Complete one Wave fully before starting the next

## Scaling

| Scope | Teams per Wave | Tasks/Team |
|-------|---------------|------------|
| Small feature | 2 | 3-5 |
| Medium feature set | 3 | 5-8 |
| Large architecture | 4 | 8-15 |

Above 4 teams, split into sequential Waves.

## Integration

**Composes with:**
- **plan** — Phase 2 implementation planning
- Git worktree workflow — Phase 3 worktree creation
- **pr** — Phase 6 merge/PR/cleanup

**Does NOT replace:**
- Sequential single-branch execution
- **execute-plan** — Teams workflow composes with it, doesn't replace it
