---
description: >-
  Generates a changelog from Conventional Commits, calculates the next semantic
  version, updates CHANGELOG.md, and optionally creates a git tag and GitHub
  Release. Every entry maps to a real commit — nothing is fabricated. Use at
  release time. Do not use for mid-development commit summaries.
argument-hint: '[--from <tag>] [--bump major|minor|patch] [--release]'
agent: agent
tools:
  - execute
  - read
  - edit
---

# Changelog

Use this prompt when you are ready to cut a release, preview what has changed
since the last release, or update `CHANGELOG.md` before tagging.

## Arguments

- `--from <tag>` — use a specific tag as the baseline instead of auto-detecting
  the most recent one
- `--bump major|minor|patch` — override the auto-calculated version bump level
- `--release` — after updating `CHANGELOG.md`, create the git tag and publish a
  GitHub Release; omit to stop after the changelog commit
- `--dry-run` — preview output without writing files, creating tags, or
  publishing releases

## Step 1: Determine Baseline

Fetch all remote tags and find the most recent version tag:

```bash
git fetch --tags origin
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
```

If `--from <tag>` was supplied, use that value as `LAST_TAG`.

If no tag exists, identify the default branch so all commits can be collected:

```bash
MAIN=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
if [ -z "$MAIN" ]; then
  git show-ref --verify --quiet refs/remotes/origin/master && MAIN=master || MAIN=main
fi
```

## Step 2: Collect Commits

Gather commits since the baseline (or all commits when there is no tag):

```bash
if [ -n "$LAST_TAG" ]; then
  git log "$LAST_TAG"..HEAD --pretty=format:"%H %s" --no-merges
else
  git log --pretty=format:"%H %s" --no-merges
fi
```

Parse each subject line against Conventional Commits format:

```
<type>[optional scope][optional !]: <description>
```

Recognised types and their changelog sections:

| Type       | Section        | Bumps |
|------------|----------------|-------|
| `feat`     | Features       | minor |
| `fix`      | Bug Fixes      | patch |
| `perf`     | Performance    | patch |
| `refactor` | Refactoring    | patch |
| `docs`     | Documentation  | —     |
| `test`     | Tests          | —     |
| `chore`    | Maintenance    | —     |
| `style`    | Style          | —     |
| `ci`       | CI/CD          | —     |
| `build`    | Build          | —     |
| `hotfix`   | Bug Fixes      | patch |

**Breaking changes:** a `!` after the type/scope, or a `BREAKING CHANGE:` footer
in the commit body, triggers a **major** bump and a dedicated section at the top
of the entry.

Commits that do not match Conventional Commits format go under "Other Changes."

## Step 3: Calculate Version

If `--bump` was supplied, apply that level directly. Otherwise auto-calculate:

1. Parse the last tag as semver (`v1.3.2` → `1.3.2`).
2. Determine the highest bump level across collected commits:
   - Any breaking change → **major** (`1.3.2` → `2.0.0`)
   - Any `feat` → **minor** (`1.3.2` → `1.4.0`)
   - Any `fix`, `perf`, `refactor`, `hotfix` → **patch** (`1.3.2` → `1.3.3`)
   - Only `docs`, `test`, `chore`, `style`, `ci`, `build` → **patch** (still a
     valid release if commits are present)
3. If no previous tag exists, start at `0.1.0`.

## Step 4: Generate Changelog Entry

Build the entry in this format:

```markdown
## [<version>] - <YYYY-MM-DD>

### Breaking Changes
- **<scope>:** <description> (<sha-short>)

### Features
- **<scope>:** <description> (<sha-short>)

### Bug Fixes
- <description> (<sha-short>)

### Performance
- <description> (<sha-short>)

### Refactoring
- <description> (<sha-short>)

### Other Changes
- <description> (<sha-short>)
```

Rules:
- Omit sections that have no entries.
- Breaking Changes always appears first when present.
- Each line includes the short SHA.
- Bold the scope when present: `**auth:** fix token refresh`.
- No scope: just the description: `fix off-by-one in pagination`.
- Never fabricate entries. Every line must trace to a real commit SHA.

## Step 5: Dry-Run Check

If `--dry-run` was specified:
- Print the generated changelog entry.
- Print the calculated version and the commit count by type.
- Do NOT write any files, create tags, or publish releases.
- Stop here.

## Step 6: Update CHANGELOG.md

Read the existing `CHANGELOG.md`. Insert the new entry at the top, after the
title line.

If `CHANGELOG.md` does not exist, create it:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [<version>] - <YYYY-MM-DD>
...
```

Check whether an entry for `<version>` is already present. If it is, do not
duplicate it — stop and report that the changelog is already up to date.

## Step 7: Commit the Changelog

```bash
git add CHANGELOG.md
git commit -m "chore(release): v<version>"
```

If `--release` was NOT supplied, stop here and report the version and commit.

## Step 8: Create Git Tag

```bash
git tag -a "v<version>" -m "v<version>"
git push origin "v<version>"
git push origin HEAD
```

## Step 9: Create GitHub Release

```bash
gh release create "v<version>" \
  --title "v<version>" \
  --notes "$(cat <<'EOF'
<changelog entry content>
EOF
)"
```

## Step 10: Report

```
Release: v<version>

  Commits:    <N> total (<breakdown by type>)
  Changelog:  CHANGELOG.md updated
  Tag:        v<version> (pushed)
  Release:    <GitHub Release URL>

  Bump:       <previous> -> <version> (<major|minor|patch>)
  Reason:     <what triggered the bump level>
```

## Key Rules

1. **Never fabricate entries.** Every changelog line must correspond to a real
   commit SHA. Non-Conventional-Commits commits go in "Other Changes" with their
   SHA.
2. **Respect `--dry-run`.** Do not write files, create tags, or publish releases
   in dry-run mode.
3. **Breaking changes are prominent.** They appear in their own section at the
   top and trigger a major bump.
4. **Idempotent.** Running this prompt twice with the same commits produces the
   same output. Do not duplicate entries already in `CHANGELOG.md`.
5. **Tag format is `v<semver>`.** Always prefix with `v`: `v1.4.0`, not `1.4.0`.
6. **Commit before tagging.** The changelog update is committed with
   `chore(release): v<version>` before the tag is created.
7. **Read `copilot-instructions.md`** for any repo-specific release conventions
   that override these defaults.
