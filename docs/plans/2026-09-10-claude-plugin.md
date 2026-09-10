---
slug: claude-plugin
source_prd: Session decisions 2026-09-10 (no PRD; the verified facts and decisions are recorded in Context and Closed Decisions below)
intent: Package the claude/ skill tree as an installable Claude Code plugin served from this repo's own marketplace, without a generated copy and without breaking the existing skills CLI install path.
type: feature
---

# Claude Code plugin from the claude/ skills

**Source:** Session decisions 2026-09-10. Facts below were verified against Claude Code 2.1.267 (`claude plugin validate`, `claude --plugin-dir`) and the official plugin reference (https://code.claude.com/docs/en/plugins-reference.md, https://code.claude.com/docs/en/plugin-marketplaces.md).

## Context

Today `claude/` is installed only by the `skills` CLI, which copies it into a target repo's `.claude/skills/`. Codex and Kimi already ship as plugins; Claude Code does not. This plan adds the Claude Code plugin.

Verified facts that shape the design:

- A plugin manifest is `.claude-plugin/plugin.json`; the only required field is `name`. The `skills` field is a path relative to the plugin root, must start with `./`, and may not leave the plugin directory. A manifest at the repo root with `"skills": "./claude/"` loads all 50 top-level skills (checked with `claude --plugin-dir`, headless). No generated copy is needed.
- Skills are namespaced `savviety-workflows:<name>` when loaded from the plugin. Nested skills (`claude/_internal/*`, `claude/test-plan/analysts/*`, `claude/test-plan/test-writer`) are not registered as invocable skills. That matches today's behaviour: all of them carry `user-invocable: false` and are read by relative path from their parent skill, which still works because they sit beside the parent inside the plugin.
- `claude plugin validate --strict` passes on every `claude/**/SKILL.md` as-is. The `model:`, `user-invocable`, `internal`, `kind`, and `private-resource` frontmatter keys raise no warnings.
- The repo-root `.claude-plugin/marketplace.json` is a Codex file (Codex adopted the Claude marketplace layout but uses `{"source": "local", "path": ...}`). Claude Code rejects it: `owner` missing, `plugins.0.source` invalid. So `claude plugin marketplace add garyld1962/savviety-skills` fails today. The two formats cannot share one file. `codex/scripts/validate_codex_assets.py` already accepts `.agents/plugins/marketplace.json` as the Codex location, and `docs/repo-skills-design.md` names it as Codex's preferred path.
- A Claude marketplace entry with `"source": "./"` (plugin root = marketplace root = repo root) validates. A marketplace without `description` fails `--strict`.
- Plugins cannot ship `settings.json` permission rules. The deny list in `claude/settings.template.json` is not part of the plugin; the `skills` CLI remains the way to install it.
- `claude plugin validate` works with an empty `CLAUDE_CONFIG_DIR`, so CI can run it without credentials.
- Four skills hard-code the `.claude/skills/` install path in their instructions: `skill-help`, `feature-sweep`, `skill-audit`, `drawio`. Under the plugin the skills root is `<plugin-root>/claude/`, so those instructions must resolve the root from the skill's own base directory instead.

Scope: repo-root manifests, the Codex marketplace move, the four path rewrites, CI, tests, and docs. `manifest.json`, `cli/skill.sh`, the `.claude/skills/` overlay, `codex/`, `copilot/`, and `hermes/` content are not touched; `kimi/skills/` changes only through the existing `bin/build-kimi-plugin` regeneration. `codex/templates/marketplace.json` (installed into target repos by `skills --codex`) is unchanged.

## Closed Decisions

- Plugin root is the repo root, with `"skills": "./claude/"`. No build script, no generated tree; `claude/` stays the single source.
- Plugin name is `savviety-workflows`, version `0.2.0`, matching the Codex and Kimi plugins. Marketplace name is `savviety`; the installed id is `savviety-workflows@savviety`.
- This repo's own Codex marketplace moves to `.agents/plugins/marketplace.json`; `.claude-plugin/marketplace.json` becomes the Claude Code marketplace. The target-repo Codex install path in `manifest.json` is unchanged.
- The four skills that hard-code `.claude/skills/` are rewritten to derive the skills root from the directory their own SKILL.md was loaded from, naming both install layouts. No other skill body changes.
- CI installs `@anthropic-ai/claude-code` with npm and runs `claude plugin validate --strict` on both manifests. A Python unittest covers the structural facts that do not need the CLI.
- No release tag is created by this plan. The final task proves `claude plugin tag --dry-run` agrees with the manifests and documents the release step.
- Permissions: README states that the plugin does not install the deny list and points to `skills --claude` for it.

## Task 1: Move the repo's Codex marketplace to `.agents/plugins/marketplace.json`

```yaml
depends_on: []
write_scope:
  - .agents/**
  - .claude-plugin/marketplace.json
  - codex/README.md
  - docs/repo-skills-design.md
milestone_end: false
```

Move the file with git so history follows it, keep its content byte-identical, and update the two documents that name its location.

Steps:

1. `mkdir -p .agents/plugins && git mv .claude-plugin/marketplace.json .agents/plugins/marketplace.json`
2. In `codex/README.md`, replace the line

   `The repo marketplace is `.claude-plugin/marketplace.json`; it points at `./codex/plugins/savviety-workflows`.`

   with

   `The repo marketplace is `.agents/plugins/marketplace.json`; it points at `./codex/plugins/savviety-workflows`. (`.claude-plugin/marketplace.json` is the Claude Code marketplace and uses a different `source` format.)`
3. In `docs/repo-skills-design.md`, replace the paragraph beginning `` `.agents/plugins/marketplace.json` is the preferred Codex marketplace location, `` with:

   `This repo keeps its own Codex marketplace at `.agents/plugins/marketplace.json` (Codex's preferred location) because `.claude-plugin/marketplace.json` is reserved for the Claude Code marketplace, whose `source` schema Codex's `local` entries do not satisfy. Target repos still receive `.claude-plugin/marketplace.json` from the installer (step 8 above); Codex reads both locations.`
4. Run `python3 codex/scripts/validate_codex_assets.py` and `python3 bin/validate-native-parity`.
5. Commit: `Move repo Codex marketplace to .agents/plugins`

**Acceptance:**
- `test -f .agents/plugins/marketplace.json`
- `test ! -e .claude-plugin/marketplace.json`
- `git log --oneline --follow -- .agents/plugins/marketplace.json | grep -q 'Cross-platform AI coding skills'` (history follows the rename)
- `jq -e '.plugins[0].source.path == "./codex/plugins/savviety-workflows"' .agents/plugins/marketplace.json`
- `python3 codex/scripts/validate_codex_assets.py`
- `python3 bin/validate-native-parity`
- `grep -q '\.agents/plugins/marketplace.json' codex/README.md`
- `! grep -q 'workspace `.agents/` directory is read-only' docs/repo-skills-design.md`

## Task 2: Add the Claude Code plugin and marketplace manifests

```yaml
depends_on: [1]
write_scope:
  - .claude-plugin/plugin.json
  - .claude-plugin/marketplace.json
milestone_end: false
```

Create both files with exactly this content.

`.claude-plugin/plugin.json`:

```json
{
  "name": "savviety-workflows",
  "version": "0.2.0",
  "description": "Savviety engineering workflows for Claude Code: PRD creation and validation, plan execution, adversarial and domain review, checkpoint, and delivery.",
  "author": { "name": "Savviety", "url": "https://savviety.com" },
  "homepage": "https://github.com/garyld1962/savviety-skills",
  "repository": "https://github.com/garyld1962/savviety-skills",
  "license": "MIT",
  "keywords": ["workflow", "planning", "review", "delivery", "savviety"],
  "skills": "./claude/"
}
```

`.claude-plugin/marketplace.json`:

```json
{
  "name": "savviety",
  "description": "Savviety skills for Claude Code.",
  "owner": { "name": "Savviety", "url": "https://savviety.com" },
  "plugins": [
    {
      "name": "savviety-workflows",
      "source": "./",
      "description": "Savviety engineering workflows for Claude Code: PRD creation and validation, plan execution, adversarial and domain review, checkpoint, and delivery.",
      "version": "0.2.0",
      "category": "productivity",
      "keywords": ["workflow", "planning", "review", "delivery", "savviety"]
    }
  ]
}
```

Then run the live load check once, from the repo root:

```bash
claude --plugin-dir . -p "Reply with only the integer count of skills available to you whose name starts with 'savviety-workflows:'." --model haiku --max-turns 1 --output-format text < /dev/null
```

Expected output: `50`.

Commit: `Add Claude Code plugin and marketplace manifests`

**Acceptance:**
- `jq -e '.name == "savviety-workflows" and .version == "0.2.0" and .skills == "./claude/"' .claude-plugin/plugin.json`
- `jq -e '.name == "savviety" and .owner.name == "Savviety" and .plugins[0].source == "./" and .plugins[0].name == "savviety-workflows"' .claude-plugin/marketplace.json`
- `claude plugin validate --strict .claude-plugin/plugin.json`
- `claude plugin validate --strict .claude-plugin/marketplace.json`
- `claude plugin validate --strict .`
- `test "$(claude --plugin-dir . -p "Reply with only the integer count of skills available to you whose name starts with 'savviety-workflows:'." --model haiku --max-turns 1 --output-format text < /dev/null | tr -dc 0-9)" = 50`

## Task 3: Resolve the skills root from the skill's own directory in the four hard-coded skills

```yaml
depends_on: []
write_scope:
  - claude/skill-help/SKILL.md
  - claude/feature-sweep/SKILL.md
  - claude/skill-audit/SKILL.md
  - claude/drawio/SKILL.md
  - kimi/skills/skill-help/**
  - kimi/skills/feature-sweep/**
  - kimi/skills/skill-audit/**
  - kimi/skills/drawio/**
milestone_end: false
```

Each of these skills tells the model to look in `.claude/skills/`. Under the plugin the same files live at `<plugin-root>/claude/`. Rewrite them so the model first locates the skills root as the parent of the directory this SKILL.md was loaded from, then uses that root. Keep every other line untouched.

**`claude/skill-help/SKILL.md`**

Replace the List Mode step 1 paragraph (starts `1. **Discover skills.**`) with:

```markdown
1. **Locate the skills root.** This file was loaded from `<skills-root>/skill-help/SKILL.md`; the skills root is its parent directory. It is `.claude/skills/` when installed by the `skills` CLI and `<plugin-root>/claude/` when loaded from the `savviety-workflows` plugin. Then **discover skills**: find all top-level SKILL.md files at `<skills-root>/*/SKILL.md` — these are user-invokable skills. Do NOT include nested sub-skills (specialists, analysts, writers under a parent skill directory) — those are internal to skill workflows.
```

Replace Detail Mode step 1 (starts `1. **Find the skill.**`) with:

```markdown
1. **Find the skill.** Resolve the skills root as in List Mode, then look for `<skills-root>/<name>/SKILL.md`. If not found, search case-insensitively and suggest the closest match.
```

Replace the Rules bullet starting `- **User-invokable only.**` with:

```markdown
- **User-invokable only.** Only list skills at `<skills-root>/*/SKILL.md` (depth 1) unless frontmatter says `user-invocable: false`. Never list `_internal`, specialists, analysts, foundations, or writers nested under a parent skill.
```

**`claude/feature-sweep/SKILL.md`**

Replace the Phase 1 block from `List all installed skills:` through the sentence ending `filter to that one skill.` with:

```markdown
Locate the skills root: this file was loaded from `<skills-root>/feature-sweep/SKILL.md`, so the skills root is its parent directory (`.claude/skills/` for a `skills` CLI install, `<plugin-root>/claude/` for the `savviety-workflows` plugin). List the installed skills:

```bash
ls "<skills-root>"
```

If the root has no other skills (a standalone copy), fall back to `.claude/skills/` and then `~/.claude/skills/`. Build a list of skill names. If `--skill` was passed, filter to that one skill.
```

In the Contract section, replace `- **Inputs:** installed skills in `.claude/skills/` (or `~/.claude/skills/`).` with `- **Inputs:** installed skills under the skills root resolved in Phase 1.` keeping the rest of the bullet.

**`claude/skill-audit/SKILL.md`**

In section 1b, replace the `# Project-level skills` comment and its `find` line with:

```bash
# Skills root of this install: the parent of the directory this SKILL.md was loaded from
# (.claude/skills for a `skills` CLI install; <plugin-root>/claude for the savviety-workflows plugin)
find "<skills-root>" -name 'SKILL.md' 2>/dev/null
```

Replace the `diff <(ls ~/repos/skills/claude/) <(ls .claude/skills/ | grep -v _project)` line with `diff <(ls ~/repos/skills/claude/) <(ls "<skills-root>" | grep -v _project)`.

**`claude/drawio/SKILL.md`**

Insert before the `**Global (all projects):**` heading:

```markdown
**Plugin (recommended):** install the `savviety-workflows` plugin from the `savviety` marketplace; this skill ships inside it and needs no copying.

```

Leave the two copy blocks as they are.

Commit: `Resolve skills root from skill directory in path-dependent skills`

**Acceptance:**
- `grep -c '<skills-root>' claude/skill-help/SKILL.md | grep -qx 4`
- `! grep -q '\.claude/skills/<name>/SKILL.md' claude/skill-help/SKILL.md`
- `grep -q 'ls "<skills-root>"' claude/feature-sweep/SKILL.md`
- `grep -q 'skills root resolved in Phase 1' claude/feature-sweep/SKILL.md`
- `grep -q 'find "<skills-root>" -name' claude/skill-audit/SKILL.md`
- `! grep -q 'find \.claude/skills -name' claude/skill-audit/SKILL.md`
- `grep -q 'savviety-workflows' claude/drawio/SKILL.md`
- `python3 bin/validate-native-parity`
- `bin/build-kimi-plugin --check` (run `bin/build-kimi-plugin` first and commit the regenerated `kimi/skills/` for these four skills; the Kimi tree is generated from `claude/`)

## Task 4: Add CI validation and a structural unit test

```yaml
depends_on: [2]
write_scope:
  - .github/workflows/ci.yml
  - tests/test_claude_plugin.py
milestone_end: false
```

In `.github/workflows/ci.yml`, after the step `- run: jq empty kimi/kimi.plugin.json`, add:

```yaml
      - run: jq empty .claude-plugin/plugin.json .claude-plugin/marketplace.json .agents/plugins/marketplace.json
      - name: Install Claude Code CLI for plugin validation
        run: npm install -g @anthropic-ai/claude-code
      - run: claude plugin validate --strict .claude-plugin/plugin.json
        env: { CLAUDE_CONFIG_DIR: /tmp/claude-ci-config }
      - run: claude plugin validate --strict .claude-plugin/marketplace.json
        env: { CLAUDE_CONFIG_DIR: /tmp/claude-ci-config }
```

Create `tests/test_claude_plugin.py`:

```python
"""Structural checks for the Claude Code plugin manifests at the repo root."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
MARKET = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
CODEX_MARKET = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())


class ClaudePluginTests(unittest.TestCase):
    def test_manifest_and_marketplace_agree(self):
        entry = MARKET["plugins"][0]
        self.assertEqual(PLUGIN["name"], entry["name"])
        self.assertEqual(PLUGIN["version"], entry["version"])
        self.assertEqual(entry["source"], "./")
        self.assertIn("name", MARKET["owner"])
        self.assertTrue(MARKET.get("description"))

    def test_skills_path_is_relative_and_inside_repo(self):
        skills = PLUGIN["skills"]
        self.assertTrue(skills.startswith("./"))
        self.assertNotIn("..", skills)
        self.assertTrue((ROOT / skills).is_dir())

    def test_every_top_level_skill_has_matching_name(self):
        for path in sorted((ROOT / PLUGIN["skills"]).glob("*/SKILL.md")):
            text = path.read_text(encoding="utf-8")
            match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
            self.assertIsNotNone(match, path)
            names = re.findall(r"^name:\s*(\S+)\s*$", match.group(1), re.M)
            self.assertEqual(names, [path.parent.name], path)

    def test_no_skill_hard_codes_the_cli_install_path_for_discovery(self):
        for name in ("skill-help", "feature-sweep", "skill-audit"):
            text = (ROOT / "claude" / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("<skills-root>", text, name)

    def test_codex_marketplace_is_separate_and_still_points_at_codex_plugin(self):
        self.assertEqual(
            CODEX_MARKET["plugins"][0]["source"]["path"], "./codex/plugins/savviety-workflows"
        )
        self.assertNotEqual(MARKET["plugins"][0]["source"], CODEX_MARKET["plugins"][0]["source"])


if __name__ == "__main__":
    unittest.main()
```

Run `python3 -m unittest tests.test_claude_plugin -v`; expected: 5 tests, OK. Note the fourth test also depends on Task 3; if Task 3 has not merged yet when this runs in isolation, it fails on purpose and passes once both land. Commit: `Validate Claude plugin manifests in CI and tests`

**Acceptance:**
- `python3 -m unittest tests.test_claude_plugin -v` exits 0 with `Ran 5 tests`
- `python3 -m unittest discover -s tests` exits 0
- `grep -q 'claude plugin validate --strict .claude-plugin/plugin.json' .github/workflows/ci.yml`
- `grep -q 'claude plugin validate --strict .claude-plugin/marketplace.json' .github/workflows/ci.yml`
- `grep -q '@anthropic-ai/claude-code' .github/workflows/ci.yml`
- `python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/ci.yml'))"`

## Task 5: Document the plugin install path and the permissions gap

```yaml
depends_on: [2, 3]
write_scope:
  - README.md
  - claude/README.md
milestone_end: false
```

In `README.md`:

1. In the platform table, change the Claude Code row's Target Environment cell from `` `.claude/skills/` `` to `` `.claude/skills/` (skills CLI) or `savviety-workflows` plugin ``, and the Codex row's cell from `` `.codex/`, `.claude-plugin/marketplace.json`, `AGENTS.md` `` to `` `.codex/`, `.claude-plugin/marketplace.json` (in target repos), `AGENTS.md` ``.
2. In the Deployment section, insert this subsection immediately before the paragraph beginning `For Claude Code, user-facing skill directories and `_internal/` map into`:

```markdown
### Claude Code plugin

The repo root is also a Claude Code plugin (`.claude-plugin/plugin.json`) served by
the `savviety` marketplace (`.claude-plugin/marketplace.json`). Installing it loads
every skill under `claude/` as `savviety-workflows:<name>` without copying files:

```bash
claude plugin marketplace add garyld1962/savviety-skills
claude plugin install savviety-workflows@savviety
```

To try a working copy before publishing, run `claude --plugin-dir /path/to/savviety-skills`.
`claude plugin validate --strict .claude-plugin/plugin.json` checks the manifest;
CI runs the same check.

The plugin does not install `claude/settings.template.json`. Its deny list
(force-push, hard reset, branch deletion guards) is only applied by
`skills --claude`, so plugin users who want it should run that installer as well or
copy the rules into `.claude/settings.json` by hand.

Releases are tagged with `claude plugin tag --push` after bumping `version` in both
manifests; `claude plugin tag --dry-run` shows the tag it would create.

This repo's own Codex marketplace lives at `.agents/plugins/marketplace.json`; the
root `.claude-plugin/marketplace.json` is Claude-only. Target repos still receive the
Codex marketplace at `.claude-plugin/marketplace.json` from `skills --codex`.
```

In `claude/README.md`, after the mapping table (the table whose rows start `` `claude/<skill>/` ``), add one paragraph:

```markdown
When loaded as the `savviety-workflows` plugin, `claude/` itself is the skills root and
nothing is copied; skills are invoked as `savviety-workflows:<name>`. Skills that need
the skills root (`skill-help`, `feature-sweep`, `skill-audit`) derive it from their own
directory so both layouts work.
```

Commit: `Document the Claude Code plugin install and permissions gap`

**Acceptance:**
- `grep -q 'claude plugin marketplace add garyld1962/savviety-skills' README.md`
- `grep -q 'claude plugin install savviety-workflows@savviety' README.md`
- `grep -q 'does not install `claude/settings.template.json`' README.md`
- `grep -q '\.agents/plugins/marketplace.json' README.md`
- `grep -q 'savviety-workflows:<name>' claude/README.md`
- `jq empty manifest.json`

## Task 6: Prove the release path and close the milestone

```yaml
depends_on: [1, 2, 3, 4, 5]
write_scope:
  - .claude-plugin/**
milestone_end: true
```

No file changes. From a clean working tree on the integration branch, confirm the full CI command set passes locally and that the tag command agrees with both manifests without creating anything.

Steps:

1. `git status --porcelain` must print nothing.
2. Run the CI set: `find claude -name "*.mjs" -print0 | xargs -0 bin/check-workflow-syntax && jq empty manifest.json claude/settings.template.json kimi/kimi.plugin.json .claude-plugin/plugin.json .claude-plugin/marketplace.json .agents/plugins/marketplace.json && bin/build-kimi-plugin --check && python3 codex/scripts/validate_codex_assets.py && bin/sync-native-contracts --check && python3 bin/validate-native-parity && python3 -m unittest discover -s tests`
3. `claude plugin tag --dry-run .` and read the printed tag name.
4. Do not create or push the tag; that is a user action after merge.

**Acceptance:**
- `test -z "$(git status --porcelain)"`
- `claude plugin validate --strict .`
- `claude plugin tag --dry-run . | grep -q 'savviety-workflows--v0.2.0'`
- `python3 -m unittest discover -s tests` exits 0
- `bin/build-kimi-plugin --check`
- `python3 codex/scripts/validate_codex_assets.py`
