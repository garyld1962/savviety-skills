# Git Audit — Report Format

Emit this structure after all checks complete. Use markdown formatting.

---

## Template

```
## Git Audit — [repo name or path]
[date]

### Summary
Score: [N]/100 ([Grade] — [Label])

| Severity | Count |
|----------|-------|
| Critical | N |
| Error    | N |
| Warning  | N |
| Info     | N |

---

### Findings

#### [CRITICAL/ERROR/WARNING/INFO] [Check name]
**Found**: [exact output or file:line that triggered this]
**Why it matters**: [one sentence from criteria.md or sharp edges]
**Fix**:
```[bash command or action]```

[repeat for each finding, grouped by severity, critical first]

---

### Passed Checks
- [check name] — [one-line confirmation]
[list all checks that found nothing]

---

### Skipped Checks
- [check name] — [reason: missing tool, empty repo, etc.]
```

---

## Example

```
## Git Audit — myapp
2026-04-21

### Summary
Score: 62/100 (C — Needs attention)

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Error    | 2 |
| Warning  | 4 |
| Info     | 1 |

---

### Findings

#### ERROR — Sensitive file tracked
**Found**: `git ls-files` returned `.env.local`
**Why it matters**: Secrets committed to history persist even after deletion — rotation required.
**Fix**:
```bash
git rm --cached .env.local
echo ".env.local" >> .gitignore
git commit -m "chore: stop tracking .env.local"
# Also rotate any secrets that were in that file
```

#### ERROR — Force push without --force-with-lease
**Found**: `scripts/deploy.sh:14` — `git push --force origin main`
**Why it matters**: Ignores remote state — can overwrite a teammate's push silently.
**Fix**:
```bash
# Replace in scripts/deploy.sh:
git push --force-with-lease origin main
```

#### WARNING — Generic commit messages (6 found)
**Found**: `git log` returned: "fix", "wip", "update", "fix", "test", "misc" in last 50 commits
**Why it matters**: Unusable for blame, bisect, and changelogs.
**Fix**: No retroactive fix needed. Use conventional commits going forward:
```bash
git commit -m "fix(auth): prevent session timeout during checkout"
```

#### WARNING — Long-lived branch: feature/old-experiment (47 days)
**Found**: `git for-each-ref` shows last commit 2026-03-05
**Why it matters**: Diverged branches accumulate merge conflicts and rot.
**Fix**: Merge, delete, or explicitly archive:
```bash
git branch -d feature/old-experiment
git push origin --delete feature/old-experiment
```

---

### Passed Checks
- .gitignore present — found at repo root
- No conflict markers — clean across all tracked files
- No node_modules committed
- No binary files over 5MB

---

### Skipped Checks
- Branch protection rules — `gh` CLI not authenticated
```

---

## Formatting Rules

- Always show the **exact command output** that triggered a finding, not a paraphrase.
- Every finding must have a **Fix** section with a runnable command or a concrete action.
- List **Passed Checks** — an audit that only shows failures is less trustworthy.
- List **Skipped Checks** so the user knows what wasn't covered.
- Keep findings terse. One "Why it matters" sentence. No paragraphs.

## Truncation Rules

These rules exist to prevent context bloat.

- **Found field**: show at most 3 lines of command output. If more matches exist, append `(N total — showing 3)`.
- **Passed Checks**: if more than 8 checks passed, collapse to a single line: `All N remaining checks passed.`
- **Do not quote the command** that was run in the finding — only quote the output it produced.
- **Do not include the full git log** in any finding. One representative commit hash + message is sufficient.
- **No preamble**: do not introduce the report with "I've completed the audit..." or similar. Start directly with the `## Git Audit` header.
