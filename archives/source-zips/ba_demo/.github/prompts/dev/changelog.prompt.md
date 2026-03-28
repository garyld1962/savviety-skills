---
description: "Generate a changelog and GitHub Release from Conventional Commits: collect commits since last tag, group by type, write CHANGELOG.md entry, tag, and create a GitHub Release."
argument-hint: "Version to release (e.g., 1.2.0) or 'auto' for auto-bump..."
---

# Changelog & Release Notes

Generate a changelog entry from Conventional Commits, tag a release, and create a GitHub Release.

## When to Use

- After merging work to main and you want to cut a release
- Need to generate release notes from commit history
- Want to update CHANGELOG.md with recent changes

## Arguments

- `<version>` — explicit version (e.g., `1.2.0`) or `auto` to auto-calculate
- `--dry-run` — preview changelog without writing files or creating tags/releases
- `--no-tag` — update CHANGELOG.md only, don't create a git tag or GitHub Release

---

## Step 1: Determine Version Range

```bash
git fetch --tags
git tag --sort=-v:refname | head -5
```

If no tags, use initial commit: `git rev-list --max-parents=0 HEAD`

## Step 2: Collect Commits

```bash
git log <since>..HEAD --oneline --no-merges
```

Parse per Conventional Commits:

| Prefix | Changelog Section |
|--------|-------------------|
| `feat` | Features |
| `fix`, `hotfix` | Bug Fixes |
| `perf` | Performance |
| `refactor` | Refactors |
| `docs` | Documentation |
| `test` | Tests |
| `build`, `ci` | Build & CI |
| `chore` | Chores |

Breaking changes (`BREAKING CHANGE:` or `feat!:`) go under **Breaking Changes**.

## Step 3: Calculate Version (if `auto`)

| Commit Types | Bump |
|-------------|------|
| Breaking change | **Major** |
| Any `feat` | **Minor** |
| Only fixes/refactors | **Patch** |

Report calculated version and ask for confirmation.

## Step 4: Generate Changelog Entry

```markdown
## [<version>] — <YYYY-MM-DD>

### Breaking Changes
- **<scope>:** <description> (<sha>)

### Features
- **<scope>:** <description> (<sha>)

### Bug Fixes
- **<scope>:** <description> (<sha>)
```

Omit empty sections.

## Step 5: Update CHANGELOG.md

If `--dry-run`: print and stop.

Insert new entry after the `# Changelog` header. If file doesn't exist, create it.

```bash
git add CHANGELOG.md
git commit -m "docs: update changelog for v<version>"
```

## Step 6: Tag (unless --no-tag)

```bash
git tag -a v<version> -m "Release v<version>"
git push origin main --follow-tags
```

## Step 7: Create GitHub Release (unless --no-tag)

```bash
gh release create v<version> --title "v<version>" --notes "<changelog entry>"
```

## Step 8: Report

```markdown
## Release Complete

**Version:** v<version>
**Tag:** v<version>
**Commits:** N (since <previous tag>)
**Changelog:** CHANGELOG.md updated
**GitHub Release:** <url>

### Summary
- Features: N
- Bug Fixes: N
- Breaking Changes: N
```

## Error Handling

| Error | Action |
|---|---|
| No commits since last tag | "Nothing to release" |
| Tag already exists | Suggest different version |
| Push rejected | Suggest rebase |
| No Conventional Commits | Group under "Other", warn |

## Key Rules

- **Conventional Commits are the source of truth.** Warn if many don't follow convention.
- **Never fabricate entries.** Every line maps to a real commit.
- **Ask before tagging.** Show version and content for approval first.
- **Breaking changes are prominent.** Always at the top.
