---
name: changelog
description: "Generate or update changelog content from git history and Conventional Commits. Use for release notes, version summaries, and tag preparation."
---

# Changelog

Generate release notes from repository changes.

## Workflow

1. Identify the previous tag with `git describe --tags --abbrev=0` when available.
2. Read commits since the previous tag, or since the branch point if no tag exists.
3. Group Conventional Commit types: `feat`, `fix`, `perf`, `refactor`, `docs`, `test`, `build`, `ci`, `chore`, and breaking changes.
4. Propose the version bump when asked to release.
5. Update `CHANGELOG.md` only when the user asks for file edits.
6. Do not create tags or GitHub releases unless explicitly requested.

## Output

Use:

- `Added`
- `Changed`
- `Fixed`
- `Removed`
- `Security`
- `Internal`

Mention the commit range used.
