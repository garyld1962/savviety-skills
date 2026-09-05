# Codex Assets

Codex-native source assets for Savviety workflows.

## Layout

- `plugins/savviety-workflows/` is the local Codex plugin.
- `agents/` contains project-scoped custom agent TOML files.
- `templates/` contains starter `AGENTS.md`, config, hooks, and rules for downstream repos.
- `prompts/` contains example prompts. Codex does not currently treat these as a first-class runtime asset.
- Each skill owns `agents/openai.yaml` for Codex UI metadata and default invocation prompts.

## Install For Local Testing

First run `./install.sh` from the source repo and open a new terminal; see the
[installation instructions](../README.md#installation). To deploy into a project:

```bash
skills --codex --init /path/to/project
skills --codex --update /path/to/project
```

The repo marketplace is `.claude-plugin/marketplace.json`; it points at `./codex/plugins/savviety-workflows`.

Restart Codex after changing plugin contents so the installed local plugin cache is refreshed.

## Authoring Rules

- Keep `SKILL.md` lean and put long rubrics or examples in `references/`.
- Skill descriptions must be trigger-heavy and boundary-heavy because Codex uses them for implicit activation.
- Skill `agents/openai.yaml` files must stay in sync with `SKILL.md`: human display name, short UI description, and `default_prompt` mentioning `$<skill-name>`.
- Keep user-specific values in templates or config, not shared skills.
- Use `.codex/agents/*.toml` only for reusable custom agents. Keep private worker prompt templates inside the skill that owns them.
- Use `.codex/rules/*.rules` for command approval policy instead of relying on prose.
- Use `skills --native-overlap` in this source tree after major plugin or built-in skill updates to find description overlap.
- Use `python3 codex/scripts/validate_codex_assets.py` before shipping Codex asset changes.

## Claude Parity Notes

- `ship` consolidates Claude `ship`, `pr`, and `hotfix`.
- `execute-prd` consolidates full PRD execution and lightweight `kickoff`.
- `skills` consolidates Claude `skill-help`, `skill-audit`, and `find-skills`.
- `grill-me` remains explicit because it is a distinct decision stress-test workflow.

## Claude functionality update (0.2.0)

The [coverage map](../docs/parity/claude-native.md) maps every public Claude workflow
onto 44 Codex entrypoints, retaining delivery/kickoff/skill-management consolidations.
Nine additional skills cover bug intake, interface comparisons, draw.io, release-feature
audits, GitHub readiness, goal discovery, issue slicing, refactor briefs and vault notes.

Plans use depends_on, write_scope and milestone_end. Older wave/lane metadata needs
explicit migration. Shared contracts are packaged inside the plugin; no sibling Claude
tree or Workflow host is required. The validators need Python 3 and PyYAML. Required
checks and reviews must prove the final code head, and manual checks remain unproved.
Existing .codex/config.toml, hooks.json and local marketplace settings are user-owned
on installer updates. Run bin/sync-native-contracts --check, the Codex asset validator,
bin/validate-native-parity and the behavioral tests before publishing changes.
