---
name: configure
description: "Resolve missing configuration for Copilot workflows, including execution environment and an Obsidian vault. Use when a workflow preflight reports missing fields; preserve existing user-owned settings."
---

# Configure

Read the repository's registry if present. Otherwise use these supplied targets:

| Target | Template/context | Destination |
|---|---|---|
| env, copilot-env | [environment template](../../templates/env.config.template.md) | user .copilot/env.config.md or project .github/instructions/env.config.md |
| vault | [vault contract](../vault/SKILL.md) | project .savviety/vault.json, or explicit user-selected path |

With no target, report configured/missing status without dumping sensitive values.
With a target, inspect existing configuration, safely discover routine defaults, and
ask only for material values that are not available. A request to configure/update
that target authorizes the scoped edit; do not reconfirm every known field. Preserve
unrelated keys, comments and user settings. Never put credentials in tracked files.
Validate the required fields and rerun the relevant preflight after writing.

## Examples
An explicit vault location can be recorded directly; a missing location needs one
question. Environment configuration must reflect actual commands and installed tools.

## Closed decisions and open decisions
Reuse the user's known paths and chosen environment. Do not invent unknown hosts,
credentials or private paths.

## Do not
Do not overwrite unrelated settings, treat examples as real user values, or claim a
configuration works without checking the relevant prerequisite.
