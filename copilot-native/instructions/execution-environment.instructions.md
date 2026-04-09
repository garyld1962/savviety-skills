---
applyTo: "**/*.{sh,bash,zsh,ps1,cmd,bat,yml,yaml,json,toml,Dockerfile,Makefile}"
description: "Cross-shell execution rules. Detect the environment first, then route commands using the user's env config or auto-detected shell syntax."
---

# Execution Environment Rules

These rules apply whenever prompts or agents generate shell commands, script guidance, or environment-specific setup steps.

## Detect Before Emitting Commands

Before recommending commands, follow the detection protocol in `.github/skills/execution-environment/SKILL.md`:

1. Detect the current shell and OS
2. Check whether the user has routing rules in `env.config.md`
3. If routing rules exist, follow them
4. If no routing rules exist, emit commands in the detected shell's native syntax

## Safety Rules

- Do not emit commands in the wrong shell syntax
- Do not assume a specific shell without detecting it
- Do not prefix commands with shell wrappers unless the user's routing rules call for it
- Do not mix path syntaxes across shell families
- Do not invent runner scripts that do not exist in the project
