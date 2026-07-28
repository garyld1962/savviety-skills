---
name: ship
description: Ship completed work through the repo's delivery flow.
---

Run `/gh-readiness` first. Then run `/skill:ship` to move the current branch through checkpoint, commit, push, PR, and release steps. When interacting with GitHub, prefer `gh` commands with `--json` output and parse with `jq`:

- `gh pr list --author @me --state open --json number,title,headRefName,url`
- `gh pr create --title "..." --body-file ... --json url,number`
- `gh release create <tag> --json url`

Pass `$ARGUMENTS` as a release or PR title hint if provided.
