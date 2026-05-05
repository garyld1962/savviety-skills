# Codex Asset Authoring

These files are source assets for downstream Codex installs.

- Prefer Codex-native terminology: skills, custom agents, plugins, hooks, rules, and `AGENTS.md`.
- Do not reference Claude tools, Claude slash-command behavior, or `.claude/settings.json` unless documenting a migration.
- Keep skills self-contained inside the plugin. A downstream install should not need the `claude/` tree.
- Put long source rubrics, schemas, and examples in `references/`.
- Keep custom agents narrow and reusable. Skill-private worker prompts belong inside that skill.
- Validate plugin manifests, skill frontmatter, TOML agents, hook JSON, and rule files before shipping.
