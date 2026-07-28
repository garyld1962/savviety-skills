# Codex Skills

Codex plugin marketplace repo for Savviety engineering skills.

## Layout

- `.claude-plugin/marketplace.json` exposes the local marketplace entry.
- `plugins/codex-skills/` is the Codex plugin root.
- `plugins/codex-skills/.codex-plugin/plugin.json` is the plugin manifest.
- `plugins/codex-skills/skills/` contains the skill packages.

## Local Install

From Codex, add this repo as a local marketplace, then install the plugin:

```bash
codex plugin marketplace add /path/to/repos/codex-skills
codex plugin add codex-skills@savviety-local
```

After pushing this repository to GitHub, Codex can also add it by Git source:

```bash
codex plugin marketplace add <owner>/codex-skills --ref main
codex plugin add codex-skills@savviety-local
```

Start a new Codex thread after installing so the skill list reloads.
