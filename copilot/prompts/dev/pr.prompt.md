---
description: >-
  Governed PR lifecycle — branch, commit, run checkpoint, push, create PR, and
  optionally squash-merge. Use when you want the full governed flow with quality
  gates. For inspecting an existing PR's state, checks, and comments, use the
  /pr built-in instead.
argument-hint: '[--draft] [--squash-merge] [--skip-checkpoint]'
agent: agent
tools:
  - execute
  - read
  - search
  - edit
---

# PR — Pull Request Lifecycle

> **Scope split:** The built-in `/pr` handles PR _inspection_ (state, comments, checks, merge readiness). This prompt handles PR _creation_ with quality gates: checkpoint → commit → push → create PR → optional merge.

Follow the skills:

- `.github/skills/repo-delivery/SKILL.md`
- `.github/skills/execution-environment/SKILL.md`

## When to Use

- Implementation is complete and ready for review or merge
- You want branch + commit + checkpoint + push + PR creation in one governed flow
- Squash-merge is the repo's standard and you want optional auto-merge

## When NOT to Use

- Repo has project-specific release steps beyond a PR — use `#ship`
- You only need the quality gate — use `#checkpoint`
- Work is not ready — finish implementation and tests first

## Arguments

- `--skip-checkpoint` — skip the checkpoint quality gate
- `--draft` — create PR as draft
- `--squash-merge` — auto-merge after PR creation using squash

## Workflow

Execute these steps in order. Stop and report if any step fails.

### Step 1: Branch Check

```bash
git branch --show-current
```

If on `main` (or the repo's default branch):
- Ask the user for a branch name
- Create and switch: `git checkout -b <branch-name>`

If already on a feature branch, continue.

### Step 2: Stage & Commit

Check for unstaged or staged changes:

```bash
git status
git diff HEAD
```

If there are changes:
- Stage relevant files: `git add <files>` (review `git status` first — avoid staging untracked build artifacts, `.zip`, `Zone.Identifier`, etc.)
- Generate a commit message from the diff (follow Conventional Commits if the project uses them; check `git log --oneline -10` for style)
- Show the commit message to the user for approval
- Commit: `git commit -m "<message>"`

If no changes and no new commits ahead of origin, stop — nothing to PR.

### Step 3: Run Checkpoint (unless --skip-checkpoint)

Invoke `#checkpoint` to run the quality gate (lint, typecheck, tests, reviews).

- If checkpoint **fails**: stop and report failures. Do not continue to push.
- If checkpoint **passes**: continue.

### Step 3.5: Security Quick Check (when warranted)

If the diff touches authentication, authorization, input handling, rendering of user content, or persistence (SQL, ORM, file I/O, deserialization), apply the security-quick-check rubric from `copilot-instructions.md` or the project's security skill if present.

Skip when the diff is purely cosmetic (formatting, comments, docs, type-only changes) or strictly internal logic with no trust boundary involvement.

- If findings are reported: stop and address them before push.
- If clean: continue.

### Step 4: Push

```bash
git push -u origin HEAD
```

If push fails (e.g., rejected), report the error. Suggest `git pull --rebase origin <branch>` if behind remote.

### Step 5: Generate PR Content

```bash
git log origin/main..HEAD --oneline
git diff origin/main..HEAD --stat
```

Auto-generate:
- **Title**: Short (under 70 chars), derived from branch name or commit messages
- **Body**: Using this format:

```markdown
## Summary
- <bullet 1: what changed>
- <bullet 2: why>
- <bullet 3: notable details, if any>

## Test plan
- [ ] <test item 1>
- [ ] <test item 2>

---
Generated with GitHub Copilot
```

**Show the title and body to the user for approval before creating the PR.** Wait for confirmation or edits.

### Step 6: Create PR

```bash
gh pr create --title "<title>" --body "$(cat <<'EOF'
<body>
EOF
)"
```

Add `--draft` if `--draft` argument was passed.

Report the PR URL to the user.

### Step 7: Merge Decision

- If `--squash-merge` was passed: proceed to merge immediately.
- Otherwise: ask the user "Merge this PR now?"

If merging:

```bash
gh pr merge <pr-number> --squash --delete-branch
git checkout main
git pull origin main
```

Report: "PR merged and branch cleaned up."

If not merging: report the PR URL and stop.

## Error Handling

- **Push rejected**: Report the error. Suggest `git pull --rebase origin <branch>` if behind remote.
- **PR already exists**: Report the existing PR URL. Ask if the user wants to update it.
- **Merge conflicts**: Report conflicts. Do not force-merge. Ask the user to resolve.
- **Checkpoint fails**: Stop before push. List failures clearly.

## Notes

- Always uses **squash merge** when merging, to keep main history clean.
- After merge, both remote and local feature branches are deleted.
- The PR body is always shown for approval — never auto-submitted without the user seeing it.
- For project-specific delivery config (CI requirements, required reviewers, branch protection), consult `skills/repo-delivery/`.
