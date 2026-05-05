# Configure Targets

Use this for Codex-side setup.

## Targets

- Repo instructions: `AGENTS.md`.
- Codex config: `.codex/config.toml`.
- Hooks: `.codex/hooks.json` and `.codex/hooks/`.
- Plugin marketplace metadata when installing local plugins.
- Skill-specific blank templates under `references/` when present.

## Rules

- Prefer filling existing templates over inventing config shape.
- Do not write secrets into tracked files.
- Preserve user-owned files unless the user asked to update them.
- Run pre-flight checks after config changes when available.

