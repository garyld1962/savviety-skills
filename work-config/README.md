# work-config

A copy of the global Claude Code config for a work laptop. It is the personal
`~/.claude/CLAUDE.md` with the kb knowledge-base section and the homelab host
table removed. Everything else is unchanged.

## Contents

| Path | Install to |
|------|------------|
| `CLAUDE.md` | `~/.claude/CLAUDE.md` |
| `skills/simplify/` | `~/.claude/skills/simplify/` |
| `skills/humanizer/` | `~/.claude/skills/humanizer/` |

The `Writing defaults` section at the end of `CLAUDE.md` references both skills
by absolute path under `~/.claude/skills/`, so the folder names must match.

## Install

```sh
mkdir -p ~/.claude/skills
cp CLAUDE.md ~/.claude/CLAUDE.md
cp -r skills/simplify ~/.claude/skills/
cp -r skills/humanizer ~/.claude/skills/
```

If a `~/.claude/CLAUDE.md` already exists, merge by hand instead of overwriting.

## Optional: RTK

`CLAUDE.md` ends with an `@RTK.md` include. RTK is a separate tool that
rewrites shell commands to trim their output. Without it the include points at
a missing file, which Claude Code ignores with a warning.

To install it:

```sh
rtk init --global
```

This writes `~/.claude/RTK.md`, installs the PreToolUse hook, and appends its
own `@RTK.md` line to `~/.claude/CLAUDE.md`. Check for a duplicate include
afterward and delete one. To skip RTK entirely, remove the `@RTK.md` line
from `CLAUDE.md`.

## Optional: ccx

The `ccx Event Log` section only activates in repos that have a
`.ccx/project.toml`. It is harmless without ccx installed. Delete the section
if ccx will not be used.

## Tools referenced in section 8

`CLAUDE.md` section 8 assumes these are on PATH: `rg`, `fd`, `jq`, `ast-grep`,
`sd`, `gh`, `uv`, `just`, `hyperfine`, `xh`, `defuddle`. Install whichever are missing.

## Provenance

- `simplify` is a local skill from this repo's author.
- `humanizer` is a third-party MIT skill by Siqi Chen, version 2.11.2. See
  `skills/humanizer/LICENSE`.
