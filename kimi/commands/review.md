---
name: review
description: Run a domain-based code review on the current diff or a PR.
---

Run `/skill:domain-review` with profile `full` on the current diff. If `$ARGUMENTS` looks like a PR reference (e.g. `#42`, `123`, or a branch name), fetch the diff using structured `gh` JSON first:

```bash
gh pr view <pr> --json number,title,body,headRefName,baseRefName,files
gh pr diff <pr>
```

Then pass the collected diff and PR description to `/skill:domain-review`.
