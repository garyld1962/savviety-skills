---
name: status
description: Show live repo state (branch, commits, PRs, stashes).
---

Run `/skill:repo-status` and summarize the current branch, working tree, unpushed commits, stashes, and open PRs. For GitHub state, use structured JSON output:

```bash
gh pr list --author @me --state open --json number,title,headRefName,updatedAt,isDraft,statusCheckRollup
gh pr view --json number,title,url,state
```

Parse the JSON with `jq` and present a concise summary.
