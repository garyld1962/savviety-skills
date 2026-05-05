# Git Audit — Criteria

Severity levels and pass/fail thresholds for each check.

---

## Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **critical** | Data loss or security risk. Immediate action required. | Block merge/deploy |
| **error** | Violates a hard rule. Must be fixed. | Fix before next PR |
| **warning** | Hygiene issue. Should be fixed soon. | Fix this sprint |
| **info** | Improvement opportunity. Low urgency. | Backlog |

---

## Commit Quality

| Check | Threshold | Severity |
|-------|-----------|----------|
| Generic commit message | Exact match to blocked list | warning |
| Commit message too short | < 10 characters | warning |
| WIP commit on main/master | Any WIP on default branch | error |
| Large commit — files changed | > 20 files | warning |
| Large commit — files changed | > 50 files | error |
| Direct commit to main (no PR) | Any in last 30 days on team repo | warning |

A repo is considered a **team repo** if `git log` shows more than one author in the last 90 days.

---

## File Hygiene

| Check | Threshold | Severity |
|-------|-----------|----------|
| .gitignore missing | Absent | warning |
| .gitignore missing + node_modules dir exists | Absent | error |
| Sensitive file tracked (.env, *.pem, *.key, etc.) | Any match | error |
| node_modules committed | Any match | error |
| Conflict markers in tracked files | Any match | critical |
| Binary file > 5MB tracked | Any match | warning |
| Binary file > 50MB tracked | Any match | error |

---

## Script Safety

| Check | Threshold | Severity |
|-------|-----------|----------|
| `git push --force` without `--force-with-lease` in scripts | Any match | error |
| `git push -f` without `--force-with-lease` in scripts | Any match | error |
| `git reset --hard origin/` in scripts | Any match | warning |
| Credentials embedded in clone URL | Any match | critical |

---

## Branch Configuration

| Check | Threshold | Severity |
|-------|-----------|----------|
| Feature branch last commit 2–4 weeks ago | Any match | warning |
| Feature branch last commit > 4 weeks ago | Any match | error |
| No branch protection on main (team repo) | Absent | warning |
| No required reviews on main (team repo) | Absent | warning |
| No required status checks on main (team repo) | Absent | warning |

---

## Scoring

After collecting all findings, compute a summary score:

```
Score = 100
  - (critical findings × 25)
  - (error findings × 10)
  - (warning findings × 3)
  - (info findings × 1)
  
Minimum score: 0
```

| Score | Grade | Label |
|-------|-------|-------|
| 90–100 | A | Healthy |
| 75–89 | B | Good |
| 60–74 | C | Needs attention |
| 40–59 | D | Poor hygiene |
| < 40 | F | Serious problems |
