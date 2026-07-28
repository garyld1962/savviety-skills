# Git Audit — Checks

---

## Commit Quality

### Message Length & Quality

```bash
# Emit only matching lines — generic messages in last 100 commits
git log --format="%h %s" -100 | grep -iE "\s(fix|wip|update|change|modify|misc|stuff|temp|tmp|asdf|test)$" | head -10
```

Flag any match. Also flag subject lines shorter than 10 characters (excluding the hash).

### Commit Size

```bash
# Emit only large commits — skip printing stats for every commit
git log --format="%H %s" -50 | while read hash msg; do
  count=$(git show --stat "$hash" | tail -1 | grep -oE "^[0-9]+")
  [ -n "$count" ] && [ "$count" -gt 20 ] && echo "$count files: $hash $msg"
done | head -10
```

Flag any match. Commits over 50 files are critical.

### Direct Commits to Main

```bash
# Non-merge commits directly on main in last 30 days
git log main --no-merges --oneline --since="30 days ago" 2>/dev/null \
  || git log master --no-merges --oneline --since="30 days ago" 2>/dev/null \
  | head -10
```

Flag if this shows recent commits (past 30 days) directly on main with no merge commits around them — suggests bypassing PR workflow.

---

## File Hygiene

### .gitignore Presence

```bash
ls .gitignore 2>/dev/null || echo "MISSING"
```

Flag as warning if absent. Flag as error if the repo has a `node_modules/` directory but no .gitignore.

### Sensitive Files Tracked

```bash
# Single pass — combine both patterns
git ls-files | grep -iE "\.(env|pem|key|p12|pfx|crt|cer)$|^(\.env(\..+)?|credentials\.json|secrets\.json)$" | head -10
```

Flag every match as an error.

### node_modules Committed

```bash
git ls-files | grep -E "^node_modules/" | head -3
```

Any match is an error. Cap at 3 — one is enough to confirm the problem.

### Conflict Markers in Tracked Files

```bash
git grep -l "<<<<<<< HEAD" 2>/dev/null | head -5
```

Any match is critical.

### Large Binary Files

```bash
# Top 5 largest tracked files — skip if slow on large repos
git ls-files | xargs -I{} git cat-file -s "HEAD:{}" 2>/dev/null \
  | paste - <(git ls-files) | sort -rn | head -5 \
  | awk '$1 > 1048576 {printf "%.1fMB %s\n", $1/1048576, $2}'
```

Flag files over 5MB as warning; over 50MB as error (should use Git LFS or external storage).

---

## Script Safety

### Force Push Without Lease

```bash
# One pass — force push without force-with-lease
grep -rn --include="*.sh" --include="*.bash" --include="*.yml" --include="*.yaml" \
  "git push" . | grep -E "\-f\b|--force\b" | grep -v "force-with-lease" | head -10
```

### Hard Reset to Remote

```bash
grep -rn --include="*.sh" --include="*.bash" "git reset --hard origin/" . | head -5
```

### Credentials in Scripts

```bash
grep -rn --include="*.sh" --include="*.bash" --include="*.yml" --include="*.yaml" \
  "git clone https://.*:.*@" . | head -5
```

Flag as error — credentials embedded in clone URLs.

---

## Branch Configuration

### Long-Lived Branches

```bash
# Only emit branches older than 2 weeks, exclude trunk branches
git for-each-ref --sort=committerdate refs/heads/ refs/remotes/ \
  --format="%(committerdate:unix) %(committerdate:relative) %(refname:short)" \
  | awk -v cutoff=$(date -d "2 weeks ago" +%s) '$1 < cutoff' \
  | grep -vE "(main|master|develop|HEAD)$" \
  | awk '{print $2, $3, $4}' | head -15
```

Flag matches older than 2 weeks as warning; older than 4 weeks as error.

### Branch Protection (requires gh CLI)

```bash
gh api repos/:owner/:repo/branches/main --jq '{
  required_reviews: .protection.required_pull_request_reviews.required_approving_review_count,
  status_checks: .protection.required_status_checks.contexts,
  enforce_admins: .protection.enforce_admins.enabled
}' 2>/dev/null
```

Flag as warning if:
- No required reviews configured
- No required status checks
- `enforce_admins` is false

Skip this check with a note if `gh` is unavailable or repo is not on GitHub.
