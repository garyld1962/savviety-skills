---
description: >-
  Fill in blank config templates for other skills. Interviews the user to
  collect required values and writes config files. Run with no argument to
  see which targets need configuring.
argument-hint: "[target name: env, workflow, ship, code-investigate, copilot-env]"
agent: "agent"
tools:
  - read
  - search
  - edit
  - execute
---

# Configure

Use this prompt to set up config files that other skills require. Each skill that
depends on user-specific or project-specific data ships a blank template with
`<FILL IN>` placeholders. This prompt reads the template, asks you for each
required value, and writes the completed config to the right location.

Use built-in `/env` when you only need a quick snapshot of the loaded
environment. Use this prompt when you need to create or refresh a config file.

Follow `.github/skills/configure/SKILL.md` when the consuming repo ships one for
the registry and detailed behavior. If no configure skill exists, use the
inline registry below.

## No-argument mode

If no target is provided, list all known targets from the project registry or
the inline registry below and show their status:

1. For each target, check whether the destination file exists and is free of
   `<FILL IN>` placeholders.
2. Show `[configured]` or `[not configured]` next to each.
3. Ask which target the user wants to configure.

## With-argument mode

1. Look up the target in the registry.
2. Read the blank template from the `template` path.
3. Scan for `<FILL IN>` and `<FILL IN: hint>` placeholders.
4. Ask the user **one question at a time** for each required field.
   - Pre-populate defaults from auto-detection where possible:
     OS (`uname -s`), shell (`$SHELL`), git remote, package manager (lock file),
     project root (`git rev-parse --show-toplevel`), existing project
     instructions or `copilot-instructions.md` sections.
   - Offer detected defaults with a confirm prompt.
5. Replace placeholders with answers and write the filled config.
6. Report what was written and which other targets remain unconfigured.

## Inline registry

Use this registry when `.github/skills/configure/SKILL.md` is not available.
This source repo currently ships only the Copilot environment template here.
Additional targets such as workflow, ship, or investigate-code should come from
the consuming repo's own configure skill or registry when those templates exist.

| Target | Template | Destination | Scope |
|---|---|---|---|
| `env` | `.github/templates/env.config.template.md` | `$HOME/.copilot/env.config.md` or `<project>/.github/instructions/env.config.md` | per-user or per-project |
| `copilot-env` | `.github/templates/env.config.template.md` | `$HOME/.copilot/env.config.md` or `<project>/.github/instructions/env.config.md` | per-user or per-project |

## Placeholder conventions

| Marker | Meaning |
|---|---|
| `<FILL IN>` | Required, must ask user |
| `<FILL IN: example>` | Required, show hint as default |
| `<OPTIONAL>` | Skip unless user volunteers |
| `# TODO: ...` | Guidance comment, remove after filling |

## CRITICAL: Do Not Guess

- Do NOT write a config file without asking the user for every required field.
- Do NOT assume a default if auto-detection fails. Ask instead.
- Do NOT overwrite an existing config without confirming.
- Do NOT hardcode shell names, hostnames, or project names. All environment
  data comes from the user's answers or auto-detection.
- Do NOT point Copilot-native users at Claude-specific config paths.
