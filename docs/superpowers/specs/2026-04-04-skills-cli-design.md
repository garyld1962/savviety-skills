# Skills CLI — Design Spec

**Date:** 2026-04-04
**Status:** Approved
**Author:** Gary + Claude

## Problem

The existing `deploy-skills` tool copies skills from `~/repos/skills` into project directories, but the name doesn't match the mental model. The workflow is "initialize a project with skills, then keep them updated" — not "deploy." Additionally, there's no way to push in-project skill edits back to the source repo.

## Solution

A Python CLI called `skills` with four commands: `init`, `add`, `update`, `push`. Replaces `deploy-skills` with clearer semantics and adds bidirectional sync.

## Commands

### `skills init`

First-time setup for a project.

1. Error if `.skills.json` already exists ("use `skills add` or `skills update`")
2. If no `--platform` flag, prompt with pick list: Claude / VS Code / Copilot / All
3. Ensure source repo exists (see Source Resolution)
4. Copy platform files:
   - Shared files: overwrite
   - Local files: copy-once (never overwrite)
   - `_project/` directories: never touched
5. Set up `.git/info/exclude` for local-only files
6. Write `.skills.json` to project root

Platform flags: `--claude`, `--vscode`, `--copilot`

### `skills add`

Add another platform's skills to an already-initialized project.

1. Require `.skills.json` — error if missing ("run `skills init` first")
2. Require `--claude`, `--vscode`, or `--copilot` flag
3. Error if platform already installed
4. Error if adding `--vscode` when `copilot` is installed (or vice versa) — mutually exclusive
5. Copy that platform's files
6. Append platform to `.skills.json`

### `skills update`

Refresh all installed platforms from the source repo.

1. Require `.skills.json`
2. `git pull` the source repo to get latest
3. Re-copy shared files for all installed platforms
4. Preserve local files and `_project/` directories
5. Update `updated_at` in `.skills.json`

### `skills push`

Push in-project skill edits back to the source repo.

1. Require `.skills.json`
2. For each installed platform, diff project files against source repo (content hash comparison, shared files only)
3. Show interactive pick list of changed files, grouped by platform
4. New files (exist in project but not in source) shown in a separate "New files" group
5. Deleted files ignored (push never deletes from source)
6. Copy selected files back to source repo
7. Print: "Changes copied to ~/repos/skills — commit and push when ready"

### All Commands

- Support `--dry-run` flag to preview without writing

## Platforms

Three platform IDs with their source and destination mappings:

| ID | Source dir | Destination | Notes |
|----|-----------|-------------|-------|
| `claude` | `claude/` | `.claude/skills/` | |
| `vscode` | `vscode/` | `.github/` (prompts, skills, agents, instructions, copilot-instructions.md) | |
| `copilot` | `copilot-native/` | `.github/` (prompts, skills, agents, instructions) | |

**Constraint:** `vscode` and `copilot` are mutually exclusive — both target `.github/` and would collide. `init` and `add` enforce this.

## Manifest — `.skills.json`

Written to the project root. Committed to git (so teammates can run `skills update`).

```json
{
  "version": 1,
  "source": "garyld1962/savviety-skills",
  "platforms": ["claude", "copilot"],
  "installed_at": "2026-04-04T10:30:00Z",
  "updated_at": "2026-04-04T10:30:00Z"
}
```

## Source Resolution

Every command ensures the source repo is available before proceeding:

1. Check `~/repos/skills` — if it exists, use it
2. If not, clone `garyld1962/savviety-skills` into `~/repos/skills`

On `update`, run `git pull` on the source repo before copying.

## File Copy Rules

### Shared Files (overwritten on init/add/update)

- Claude: `.claude/skills/<name>/` (everything except `_project/`)
- VS Code: `.github/{prompts,skills,agents,instructions}/` (except `_project/`, `personal.instructions.md`)
- Copilot: `.github/{prompts,skills,agents,instructions}/` (except `_project/`)

### Local Files (copy-once on init/add, never overwritten unless `--force-local`)

- `CLAUDE.local.md`
- `.github/copilot-instructions.md`
- `.github/instructions/personal.instructions.md`

### Protected Directories (never touched)

- `_project/` anywhere in the tree

## Git Excludes

On `init`, append rules to `.git/info/exclude`:

```
# skills-cli local files
CLAUDE.local.md
.github/copilot-instructions.md
.github/instructions/personal.instructions.md
```

## Push Diff Display

```
Changed files (claude):
  [x] review-api/SKILL.md
  [ ] checkpoint/SKILL.md

Changed files (vscode):
  [x] prompts/dev/plan.prompt.md

New files (claude):
  [ ] my-new-skill/SKILL.md

3 files selected — copy to ~/repos/skills? [y/N]
```

## Project Structure

```
skills-cli/
├── pyproject.toml
├── src/
│   └── skills_cli/
│       ├── __init__.py
│       ├── cli.py           # click group + subcommands
│       ├── config.py        # constants, paths, platform definitions
│       ├── manifest.py      # read/write .skills.json
│       ├── copier.py        # file copy logic (shared/local/project protection)
│       ├── source.py        # ensure source repo exists (local or clone)
│       └── diff.py          # compare project files vs source for push
└── tests/
```

## Dependencies

```toml
[project]
name = "skills-cli"
requires-python = ">=3.12"
dependencies = [
    "click>=8.1",
    "rich>=13.0",
]

[project.scripts]
skills = "skills_cli.cli:main"
```

Installed via `uv tool install` from local path.

- **click**: subcommand routing, flags, `--dry-run`
- **rich**: interactive checkbox pick lists, colored terminal output

## Replaces

- `~/.local/bin/deploy-skills` — superseded, can be removed after migration
- `~/repos/skills/deploy.sh` — legacy, already superseded by `deploy-skills`
