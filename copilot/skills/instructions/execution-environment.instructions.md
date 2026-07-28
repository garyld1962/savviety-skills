---
applyTo: "**/*.{sh,bash,zsh,ps1,cmd,bat,yml,yaml,json,toml,Dockerfile,Makefile}"
description: "Cross-shell execution rules for repositories used from both PowerShell and WSL. Detect the environment first, then prefer direct Linux, direct PowerShell, or explicit terminal switching before any PowerShell-to-WSL wrapper."
---

# Execution Environment Rules

These rules apply whenever prompts or agents generate shell commands, script guidance, or environment-specific setup steps.

## Detect before emitting commands

Before recommending commands, determine:

- whether the current shell is PowerShell or Linux/WSL
- whether the session is already inside WSL
- whether the repo expects Linux execution
- whether a runner script exists

## Routing rules

### If already inside WSL or Linux

- run Linux commands directly
- do not prefix with `wsl`
- use forward-slash paths

### If in PowerShell and the repo is Windows-friendly

- use PowerShell-safe commands
- avoid Bash-only syntax

### If in PowerShell and the repo expects Linux tooling

- prefer telling the user to switch to a WSL terminal or WSL-connected VS Code session
- do not emit Bash commands as if PowerShell can run them directly
- use explicit `wsl.exe` wrapping only as a last-resort fallback when the user explicitly wants that bridge

## Runner rules

- If the repo has `.scripts/run.sh`, use it only if it actually exists and the repo still relies on it
- If the repo has a PowerShell-native runner, prefer it in PowerShell mode
- Never invent a runner that does not exist

## Path rules

- Linux/WSL mode: use Linux-visible paths and forward slashes
- PowerShell mode: use PowerShell-safe path syntax
- Never mix raw Windows paths into Linux commands without conversion

## Error prevention

- Do not hardcode "the terminal is already WSL" unless detected
- Do not recommend `wsl` inside a shell that is already WSL
- Do not treat `wsl.exe -e bash -lc` as the standard answer
- Do not emit shell syntax from the wrong environment
