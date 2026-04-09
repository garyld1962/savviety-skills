---
name: execution-environment
description: Detect the current shell and OS, then choose safe command routing using the user's env config. Does not hardcode any specific shell — reads routing rules from the user's env.config.md.
---

# Execution Environment

Use this skill whenever prompts, agents, or instructions need to produce shell commands or environment-specific guidance.

## Core Principle

> Detect the execution environment first. Do not assume any specific shell or OS.

## Pre-flight Config Check

Before routing commands, check whether the user has an env config:

1. Check `$HOME/.copilot/env.config.md` (user-level) or `<project>/.github/instructions/env.config.md` (project-level).
2. If found, load the registered shells, routing rules, and host mappings.
3. If NOT found, fall back to auto-detection only (detect shell, emit commands in its native syntax). Optionally suggest:
   > "For cross-platform routing rules, run `/configure copilot-env` or copy the template from `.github/skills/execution-environment/env.config.template.md`."

## Detection Protocol

Check non-destructive signals before recommending commands:

### Shell/runtime signals

- What is the current shell? (Check `$SHELL`, process name, or shell-specific variables)
- What OS family is running? (`uname -s` or equivalent)
- Is this a remote session? (`$SSH_CONNECTION`, `$SSH_TTY`)
- Is this running inside a container or virtualized environment? (`/proc/version`, `/.dockerenv`, or equivalent markers)

### Path signals

- Forward-slash paths suggest Unix-family shells
- Backslash paths or drive letters suggest Windows-family shells

### Tooling signals

- Does the repo have runner scripts? (Check for `Makefile`, `package.json` scripts, `pyproject.toml`, shell scripts)
- Does the repo define a preferred execution pattern in its project instructions?

## Routing

After detection, match the environment against the user's config:

1. Identify which registered shell is active
2. Look up the routing rule for that shell
3. If the detected shell matches what the project expects → emit commands directly
4. If mismatch detected → follow the routing rule (direct, switch-terminal, or warn)
5. If no config exists → emit commands in the detected shell's native syntax

## Output Pattern

When environment choice matters, report:

```text
Detected shell: <detected>
OS: <os family>
Execution strategy: <direct / switch terminal / use project runner>
Reason: <brief explanation>
```

When the environment is obvious and no guidance is needed, proceed silently.

## Safety Rules

- Never emit commands in the wrong shell syntax
- Never assume a specific shell without detecting it
- Never prefix commands with shell wrappers unless the user's routing rules explicitly call for it
- Never invent runner scripts that do not exist in the project
- Never mix path syntaxes across shell families

## Relationship to Other Assets

- Put always-on routing rules in the `execution-environment.instructions.md` instruction
- Put the detection protocol in this skill
- Let prompts reference this skill instead of re-explaining shell logic
- User-specific routing rules live in `env.config.md` (not in this skill)
