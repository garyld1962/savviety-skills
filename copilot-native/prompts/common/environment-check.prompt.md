---
description: >-
  Inspect the current shell, path style, tooling, and repo conventions to
  determine whether commands should run directly in PowerShell, directly in
  WSL/Linux, or whether the user should switch terminals instead of relying on
  a PowerShell-to-WSL wrapper.
argument-hint: "[optional path or command pattern to evaluate]"
agent: "agent"
tools:
  - read
  - search
  - execute
---

# Environment Check

Use this prompt when the same repo may be used from both PowerShell and WSL and you need a safe execution strategy.

Do not use this prompt when the execution environment is already obvious and no shell-specific guidance is needed.

Follow the skill: `.github/skills/execution-environment/SKILL.md`

## What to do

Determine:

- current shell/runtime
- current path style
- whether WSL is involved
- whether the repo expects a runner script
- whether commands should run directly, or whether the user should switch terminals

## Output

Return only the fields that help resolve a real execution ambiguity:

- detected mode
- evidence
- recommended execution strategy
- whether terminal switching is preferable
- example safe command pattern

## CRITICAL: Do Not Guess

- Do NOT assume the integrated terminal is already Linux.
- Do NOT assume `wsl.exe` is required.
- Do NOT recommend `wsl.exe -e bash -lc` as the default answer.
- Do NOT emit Bash syntax in PowerShell mode.
- Do NOT emit PowerShell syntax in WSL/Linux mode.
- Do NOT force a structured environment report when a silent check is sufficient to proceed safely.
