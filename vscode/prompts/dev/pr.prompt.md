---
description: "Create or manage a pull request: branch, stage, commit, run checkpoint, push, and PR creation. Does not wait for CI or build a release — for that, use the ship skill."
---

# Pull Request Lifecycle

Automate the full PR lifecycle from branch creation through optional merge.

## When to Use

- Ready to create a PR from current changes
- Need to branch, commit, push, and open a PR
- Want automated checkpoint before push

## Arguments

- `--skip-checkpoint` — skip the checkpoint quality gate
- `--merge` — auto-merge after PR creation (skip merge prompt)
- `--no-merge` — skip merge prompt entirely (PR stays open)
- `--draft` — create PR as draft

## Workflow

### Step 1: Branch Check

```bash
git branch --show-current
```

If on `main`: ask user for branch name, create with `git checkout -b <name>`.

### Step 2: Stage & Commit

```bash
git status
git diff HEAD
```

If changes exist:
- Stage relevant files (`git add <files>` — avoid untracked junk like .exe, .zip, Zone.Identifier)
- Generate commit message (follow Conventional Commits if the project uses them)
- Show commit message to user for approval
- Commit

If no changes and no new commits ahead of origin, stop — nothing to PR.

### Step 3: Run Checkpoint (unless --skip-checkpoint)

Run the checkpoint quality gate (lint, build, tests). If checkpoint fails, stop before push.

### Step 4: Push

```bash
git push -u origin HEAD
```

### Step 5: Generate PR Content

```bash
git log origin/main..HEAD --oneline
git diff origin/main..HEAD --stat
```

Auto-generate:
- **Title**: Short (under 70 chars)
- **Body**:

```markdown
## Summary
- <what changed>
- <why>

## Test plan
- [ ] <verification items>

---
Generated with [GitHub Copilot](https://github.com/features/copilot)
```

**Show title and body to user for approval before creating.**

### Step 6: Create PR

```bash
gh pr create --title "<title>" --body "<body>"
```

Add `--draft` flag if requested.

### Step 7: Merge Decision

- `--no-merge`: done, report PR URL.
- `--merge`: proceed to merge immediately.
- Otherwise: ask user "Merge this PR now?"

If merging:
```bash
gh pr merge <pr-number> --squash --delete-branch
git checkout main
git pull origin main
```

## Error Handling

| Error | Action |
|---|---|
| Push rejected | Suggest `git pull --rebase origin <branch>` |
| PR already exists | Report existing URL, ask to update |
| Merge conflicts | Report, do not force-merge |
| Checkpoint fails | Stop before push |

## Notes

- Always uses **squash merge**
- After merge, both remote and local feature branches are deleted
- PR body is always shown for approval first
