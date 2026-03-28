---
name: execution-environment
description: Detect whether work is happening in PowerShell, WSL/Linux, or a mixed Windows+WSL setup and choose safe command, path, and script behavior without assuming one shell model.
---

# Execution Environment

Use this skill whenever prompts, agents, or instructions need to produce shell commands or environment-specific guidance.

## Core principle

> Detect the execution environment first. Do not assume WSL or PowerShell.

The same repo may be used from:

- PowerShell on Windows
- a WSL/Linux shell
- VS Code connected to WSL
- PowerShell in a repo that is better run from WSL

## Goal

Produce commands and guidance that work in the current environment without causing avoidable WSL errors, path errors, or shell syntax errors.

## Environment detection checklist

Check as many non-destructive signals as needed before recommending commands:

### Shell/runtime signals

- Is the shell PowerShell? Look for PowerShell syntax support or `$PSVersionTable`
- Is the shell Linux/WSL? Look for `uname`, `/proc/version`, or Linux-style home paths
- Is the session already inside WSL? If so, do **not** prefix commands with `wsl`

### Path signals

- Linux/WSL paths: `/home/...`, `/mnt/c/...`
- Windows paths: `C:\...`

### Tooling signals

- Does the repo have `.scripts/run.sh`?
- Does the repo have a Windows runner such as `.scripts/run.ps1` or equivalent?
- Are Linux-only commands expected by project instructions?
- Is `wsl.exe` available from PowerShell when Linux execution is required?

## Decision rules

### Case 1 — Already in Linux/WSL shell

Use Linux commands directly.

- do not add `wsl -d ...`
- use forward-slash paths
- prefer native repo paths

### Case 2 — In PowerShell and repo/tooling is Windows-native

Use PowerShell-safe commands and Windows paths or quoted relative paths as appropriate.

### Case 3 — In PowerShell but project expects Linux/WSL execution

Prefer **switching the terminal/session to WSL** instead of wrapping every command through WSL from PowerShell.

Recommended behavior:

- say that the repo/tooling expects Linux execution
- recommend opening the repo in a WSL terminal or VS Code WSL session
- avoid emitting Bash commands as if they will run correctly in PowerShell

Use explicit WSL wrapping only as a **last-resort fallback**, and only when:

- the shell is PowerShell
- the repo instructions or tooling clearly expect Linux
- the shell is not already inside WSL
- the user explicitly wants a PowerShell-to-WSL bridge command

### Case 4 — Ambiguous or mixed setup

Prefer a lightweight environment check first, then state the chosen mode before running commands.

## Safety rules

- Never blindly prefix commands with `wsl`
- Avoid `wsl.exe -e bash -lc` as a default pattern
- Never assume PowerShell syntax works in Bash or vice versa
- Never mix Windows paths into Linux commands without conversion
- Never assume a `run.sh` exists
- Never assume the integrated terminal is already WSL unless detected
- Never assume a deleted or historical runner still exists

## Path handling rules

### When using Linux/WSL commands

- use forward slashes
- use Linux-visible paths
- avoid raw `C:\...` paths

### When using PowerShell commands

- use PowerShell-safe quoting
- avoid Bash-only operators or syntax

## Runner rules

If the project defines a runner script, use it according to the detected shell model:

- `run.sh` is appropriate only if it actually exists and the repo still uses it
- a PowerShell runner should be used from PowerShell when the repo defines one

## Recommended output pattern

When environment choice matters, say:

```text
Detected mode: PowerShell / WSL / Linux
Execution strategy: direct shell / switch to WSL terminal / use repo runner / explicit WSL fallback
Why: <brief reason>
```

Then provide the commands.

## Relationship to instructions

- Put always-on routing rules in an instruction
- Put portable detection heuristics in this skill
- Let prompts reference this skill instead of re-explaining shell logic every time
