# Ship Workflow

Use this for local delivery readiness, commits, pushes, PRs, releases, and fast hotfixes.

## Default Mode

1. Confirm changed files and current branch.
2. Run `checkpoint` unless the user explicitly limits scope.
3. Run `references/security-quick-check.md` when the diff touches security-sensitive areas.
4. Prepare a commit only when requested or when the delivery workflow requires it.
5. Push only with explicit user approval.
6. Create or update a PR only with explicit user approval.
7. Report branch, commit, verification, PR URL if created, and any skipped gates.

## Release Mode

Run the default mode first, then perform release steps declared by the repo contract. Release, publish, deploy, and merge actions require explicit user approval.

## Fast Hotfix Mode

Use only for urgent production fixes. Keep scope narrow, run targeted tests, run security quick check, create a clear hotfix PR, and do not merge without explicit approval.

## Hard Rules

- Do not guess delivery commands.
- Do not push, merge, release, or deploy without explicit approval.
- Do not hide failed or skipped verification.

