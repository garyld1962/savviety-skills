---
name: pre-flight-pattern
description: >
  Reusable pattern for config-dependent prompts. Defines how to detect missing
  config files, identify unfilled placeholders, and halt with actionable
  messages before any main workflow logic runs. Auto-loaded by prompts that
  depend on user-editable config (e.g., configure, autonomous-development-kickoff).
  Defines hard and soft pre-flight modes, placeholder conventions, and the
  "configure first" redirect pattern.
---

# Pre-flight Required Config Check

This is a **pattern document**, not a user-invokable prompt. Other prompts embed this pattern by referencing it and filling in the specifics.

## When to Use

Embed this pattern in any prompt that depends on a user-editable config file. The check runs at the very start of the prompt, before any main workflow logic.

## The Pattern

Add a section like this to the top of your prompt's workflow:

---

### Pre-flight Required Config

Before proceeding, verify:

1. **File existence check.** Check whether `<config_path>` exists.

   If NOT found, halt with:
   > This prompt requires `<config_path>`.
   >
   > Set it up interactively:
   > ```
   > /configure <target>
   > ```
   >
   > Or copy the template and edit manually:
   > ```
   > cp <template_path> <config_path>
   > ```

2. **Placeholder check.** Read the config file and scan for these markers:
   - `<FILL IN>` — required field, not yet set
   - `<FILL IN:` — required field with hint, not yet set
   - `TODO` — guidance comment that should have been removed

   If ANY required placeholder remains, halt with:
   > Config at `<config_path>` has <N> unfilled required field(s):
   >
   > - `field_name_1` (line 12)
   > - `field_name_2` (line 25)
   >
   > Run `/configure <target> --recheck` to fill them in, or edit the file directly.

3. **Proceed.** If the file exists and contains no required placeholders, continue to the main workflow. Do not mention the pre-flight check in output — it should be invisible when config is healthy.

---

## Customization Points

When embedding this pattern, fill in:

| Placeholder | What to substitute |
|---|---|
| `<config_path>` | The destination path (e.g., `~/.copilot/env.config.md`) |
| `<template_path>` | The template source path (e.g., `.github/skills/env-check/env.config.template.md`) |
| `<target>` | The configure target name (e.g., `env`) |
| Required fields list | The specific `required_fields` or `required_sections` for the prompt |

## Soft vs Hard Pre-flight

- **Hard pre-flight** (default): Halt. The prompt cannot run without config.
- **Soft pre-flight**: Warn but continue. The prompt can run with argument-provided overrides. Use when the config provides defaults but invocation arguments can replace them.

For soft pre-flight, replace "halt" with:
> Config at `<config_path>` is missing. Using argument-provided values.
> To set defaults, run `/configure <target>`.

## Placeholder Conventions

All templates shipped with prompts use these markers:

| Marker | Meaning | Pre-flight behavior |
|---|---|---|
| `<FILL IN>` | Required, no default | Blocks if present |
| `<FILL IN: example>` | Required, with hint | Blocks if present |
| `<OPTIONAL>` | Not required | Ignored by pre-flight |
| `# TODO: ...` | Guidance comment | Warn but do not block |

## Example: Embedding in a Real Prompt

```markdown
## Pre-flight Required Config

Before proceeding, verify:

1. Check `~/.copilot/env.config.md` exists.
   If not: "Run `/configure env` or copy `.github/skills/env-check/env.config.template.md`."

2. Scan for `<FILL IN>` placeholders in required sections: `shells`, `routing_rules`.
   If found: list unfilled fields and suggest `/configure env --recheck`.

3. If healthy, proceed silently.
```

## Config File Locations

In Copilot prompts, config destinations follow these conventions:
- User-scoped config: `~/.copilot/` or referenced from `copilot-instructions.md`
- Template sources: `.github/skills/<skill-name>/`
- Instruction overlays: `.github/instructions/`
