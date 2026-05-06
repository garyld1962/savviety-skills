# Codex Assets

Codex-native source assets for Savviety workflows.

## Layout

- `plugins/savviety-workflows/` is the local Codex plugin.
- `agents/` contains project-scoped custom agent TOML files.
- `templates/` contains starter `AGENTS.md`, config, hooks, and rules for downstream repos.
- `prompts/` contains example prompts. Codex does not currently treat these as a first-class runtime asset.

## Install For Local Testing

The repo marketplace is `.claude-plugin/marketplace.json`; it points at `./codex/plugins/savviety-workflows`.

Restart Codex after changing plugin contents so the installed local plugin cache is refreshed.

## Authoring Rules

- Keep `SKILL.md` lean and put long rubrics or examples in `references/`.
- Skill descriptions must be trigger-heavy and boundary-heavy because Codex uses them for implicit activation.
- Keep user-specific values in templates or config, not shared skills.
- Use `.codex/agents/*.toml` only for reusable custom agents. Keep private worker prompt templates inside the skill that owns them.
- Use `.codex/rules/*.rules` for command approval policy instead of relying on prose.
- Use `skills --native-overlap` in this source tree after major plugin or built-in skill updates to find description overlap.
