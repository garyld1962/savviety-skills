---
name: gh-readiness
description: "Verify GitHub CLI (gh) is installed, authenticated, and able to reach github.com before running skills that create PRs, issues, or releases. Use before /pr, /ship, /hotfix, /issue-slices, /bug-session, or /changelog when gh status is unknown."
---

# /gh-readiness — GitHub CLI Readiness Gate

Check that the GitHub CLI is ready for commands the Savviety workflow skills rely on. This skill is read-only: it never creates or modifies anything on GitHub.

## When to Use

- Before `/pr`, `/ship`, `/hotfix`, `/issue-slices`, `/bug-session`, or `/changelog` when you are unsure whether `gh` is set up.
- After switching machines, shells, or GitHub accounts.
- When a skill that calls `gh` fails with an auth or network error.

## When NOT to Use

- You already confirmed `gh` works in this session — proceed directly.
- You are working in a repo that does not use GitHub — these checks are GitHub-specific.

## Checks (run in order)

1. **`gh` on PATH**

   ```bash
   command -v gh
   ```

   Missing → report `gh not installed` and stop.

2. **Authentication status**

   ```bash
   gh auth status
   ```

   Non-zero exit or `not logged in` → report `gh not authenticated` and stop.
   Prefer this over `gh auth token` because it also shows the active host and token source.

3. **Token scope sanity (read-only check)**

   ```bash
   gh auth status 2>&1 | grep -E "(read:org|repo|read:user|project)"
   ```

   If scopes are missing for the upcoming operation, note which ones are needed but do not fail the readiness gate unless the missing scope is definitely required for the calling skill.

4. **API reachability**

   ```bash
   gh api user --jq '.login'
   ```

   Non-zero or empty → report `cannot reach GitHub API` and stop.
   This confirms both network and token validity.

5. **Current repo remotes**

   ```bash
   git remote -v
   ```

   If no `origin` remote points to GitHub, note that PR/issue skills will fail unless a remote is added.

## Output format

```
GitHub CLI readiness: <PASS | PARTIAL | FAIL>

- gh installed:     yes / no
- authenticated:    yes / no
- active host:      github.com / <other>
- API reachable:    yes / no
- GitHub remote:    yes / no
- scopes:           <list or note>

Next steps:
  <PASS>    gh is ready; proceed with /pr, /ship, /issue-slices, etc.
  <PARTIAL> gh works but a required scope or remote is missing; see notes above.
  <FAIL>    run `gh auth login` (or `gh auth refresh -s <scope>`) and retry.
```

## Integration with other skills

Other skills should call `/gh-readiness` as a pre-flight gate when `gh` is required:

- `/pr`, `/ship`, `/hotfix` — require `repo` scope.
- `/issue-slices`, `/bug-session` — require `repo` scope.
- `/changelog` when releasing — requires `repo` scope.

Do not call this skill inside tight loops or after every command; run it once at the start of a GitHub-dependent workflow.

## Failure modes

- `gh not installed` → user must install GitHub CLI.
- `gh not authenticated` → user must run `gh auth login`.
- `missing scope` → user must run `gh auth refresh -s <scope>`.
- `cannot reach GitHub API` → check network, proxy, or token expiry.
- `no GitHub remote` → run `git remote add origin <url>`.
