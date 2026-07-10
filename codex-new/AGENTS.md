# Codex Asset Authoring

These files are source assets for downstream Codex installs.

## Where to edit

- `plugins/savviety-workflows/skills/<name>/SKILL.md` contains user-invocable skill entrypoints.
- `plugins/savviety-workflows/skills/<name>/agents/openai.yaml` contains UI metadata for each skill.
- Put long rubrics, schemas, and examples in `plugins/savviety-workflows/skills/<name>/references/`.
- Put skill-private worker prompts inside that skill package. Put reusable custom agents in top-level `agents/*.toml`.
- Templates for downstream repos live in `templates/`; they should not contain machine-specific values.

## Authoring rules

- Prefer Codex-native terminology: skills, custom agents, plugins, hooks, rules, and `AGENTS.md`.
- Do not reference Claude tools, Claude slash-command behavior, or `.claude/settings.json` unless documenting a migration.
- Keep skills self-contained inside the plugin. A downstream install should not need the `claude/` tree.
- Put long source rubrics, schemas, and examples in `references/`.
- Keep custom agents narrow and reusable. Skill-private worker prompts belong inside that skill.
- Validate plugin manifests, skill frontmatter, TOML agents, hook JSON, and rule files before shipping.
- Frontmatter `name:` must match the skill directory.
- `description:` is trigger surface. Include concrete phrases, boundaries, and handoffs to competing skills.
- Each user-invokable skill needs `agents/openai.yaml` with `interface.display_name`, a 25-64 character `short_description`, and a `default_prompt` that names `$<skill-name>`.
- Add a `When Not To Use` or relationship section when a skill overlaps with built-in Codex behavior or another installed plugin.
- Keep legacy Claude material out of normal navigation. If retained for migration, store it under `references/legacy/` and state that it is archival only.

## Diagnosing skill misfires

Wrong-skill activation is usually a description problem, not an install problem.

1. Confirm the skill exists under `plugins/savviety-workflows/skills/<name>/SKILL.md`.
2. Compare its `description:` with the user's phrasing and nearby competing skills.
3. Tighten the description with explicit trigger phrases and boundary language.
4. Add a handoff in the body when another skill should win.
5. Run `python3 scripts/validate_codex_assets.py` before shipping.

## Cross-platform notes

The neighboring platform trees are independent source assets. Changes in `../claude` do not automatically port here. Review recent upstream skill changes for concepts, then rewrite them in Codex-native terms and structure.
