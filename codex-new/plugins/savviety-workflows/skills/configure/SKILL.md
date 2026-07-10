---
name: configure
description: "Fill missing project or user configuration required by Savviety workflow skills. Use when a pre-flight check reports placeholders or missing config."
---

# Configure

Use this when a workflow needs configuration before it can run.

Read `references/pre-flight-check.md` for the pre-flight contract and `references/targets.md` for Codex config targets. `references/legacy/` is archival only.

## Workflow

1. Identify the config file and missing fields.
2. Ask only for values that cannot be discovered safely.
3. Write config only inside the target repo or approved user config path.
4. Never embed tokens, passwords, or personal secrets in shared repo files.
5. Re-run the pre-flight check after editing.
