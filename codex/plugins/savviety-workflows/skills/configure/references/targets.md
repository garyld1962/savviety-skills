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


## Obsidian vault

For the vault target, resolve an explicit path or OBSIDIAN_VAULT first. Otherwise
write user-owned .savviety/vault.json using the sibling vault skill contract.
Ask once for an unknown location, preserve existing fields, and verify directory access.

## jev-gate (System-1 Decision Control Plane)

- `jev-gate-global`: User-global config at `~/.config/jev-gate/config.toml` (RTX 5090 `/v1/systemone` endpoint, default `fast_lane`/`deep_lane` mappings, `global_blocklist`, and baseline thresholds).
- `jev-gate`: Project-local override at `{project}/.jev-gate.toml` (`invariants` list of plain-sentence rules evaluated against `git diff`, `search.domain_allowlists`, and optional `[thresholds]`; the server rejects unknown keys).
- Precedence is always `Runtime Tool Args > ./.jev-gate.toml > ~/.config/jev-gate/config.toml`.
