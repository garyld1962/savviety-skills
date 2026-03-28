---
description: "Ship changes end-to-end: commit, PR, CI, merge, and release build. One command from working tree to merged PR."
---

# Ship It

End-to-end ship: commit, PR, CI, merge, build installer. One command to go from working tree changes to a merged PR with release binary.

## When to Use

- All work is done and you want to ship everything in one go
- Want commit → push → PR → CI → merge → build in a single flow

## Arguments

- `--skip-checkpoint` — skip quality gate before push
- `--skip-build` — skip installer release build after merge
- `--draft` — create PR as draft and stop (no merge)

## Workflow

### Step 1: Branch
```bash
git branch --show-current
```
If on `main`: ask user for branch name, create with `git checkout -b <name>`.

### Step 2: Stage & Commit
```bash
git status
git diff HEAD
git log --oneline -5
```
If changes exist: stage relevant files (avoid untracked junk), generate Conventional Commits message, commit. If no changes and no commits ahead of origin: stop.

### Step 3: Quality Gate (unless --skip-checkpoint)
Run the checkpoint quality gate. If it fails, stop before push.

### Step 4: Push & Create PR
```bash
git push -u origin HEAD
```
Generate PR title and body, create with `gh pr create`. If `--draft`, stop here.

### Step 5: Wait for CI
```bash
gh pr checks <number> --watch
```
If CI fails: report the failure URL, stop, do not merge.

### Step 6: Squash Merge
```bash
gh pr merge <number> --squash --admin
```
If merge fails: report error and stop.

### Step 7: Pull Main
```bash
git checkout main
git pull
```

### Step 8: Report
```
## Ship Complete

**Branch:** <branch-name>
**PR:** #<number> — <title>
**Commit on main:** <sha>
**CI:** PASS
```

### Step 9: Build Installer (unless --skip-build)
```bash
cd tools/installer && cargo build --release
```
Report binary location and size.

## Error Handling

| Error | Action |
|---|---|
| Push rejected | Suggest `git pull --rebase origin <branch>` |
| PR already exists | Report existing URL |
| CI fails | Report failure URL, stop |
| Merge blocked | Report reason (conflicts, reviews), stop |
| Cargo build fails | Report error, suggest `cargo test` first |

## Notes

- Always squash-merge to keep main clean
- Uses `--admin` on merge to bypass branch protection (repo owner workflow)
- Installer build is Rust — expects working cargo toolchain
