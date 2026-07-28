# CLAUDE.md — claude/ (skills development source)

This is the source-of-truth tree for Claude Code skills. **Edit here. Test elsewhere.**

## Where you are

```
~/repos/savviety-skills/
├── claude/         ← YOU ARE HERE — Claude Code skills source
├── codex/          Codex-native plugin/agents/templates
├── copilot/        Copilot Native (.github/) source
├── kimi/           Kimi overlay (sources skills from claude/ via manifest)
├── manifest.json   Install manifest consumed by cli/skill.sh
└── cli/skill.sh    Installer
```

## Edit vs test

Tests do not run in this repo. They run in a separate harness:

| Action | Path |
|--------|------|
| Edit a skill | `claude/<skill-name>/SKILL.md` (here) |
| Test it | `cd ~/repos/skills-test-harness/claude-test && claude /<skill-name>` |

The harness was seeded as a copy on 2026-05-05. After editing a skill here, sync into the harness before testing:

```
~/repos/savviety-skills/cli/skill.sh --claude --update ~/repos/skills-test-harness/claude-test
```

Or, for a one-off, copy the skill dir directly into `~/repos/skills-test-harness/claude-test/.claude/skills/`. The harness also has `codex-test/`, `copilot-test/`, and `kimi-test/` siblings for cross-platform testing.

## What lives in `claude/`

- `<skill-name>/SKILL.md` — user-invocable skills (top-level dir per skill)
- `_internal/` — contracts and rubrics, `user-invocable: false`, called by other skills
- `infra/` — hook scripts (installed to `.claude/{pr-guardrail,journal,install-scan}`, NOT to `.claude/skills/`)
- `MODEL-POLICY.md`, `SESSION-CONTEXT.md`, `README.md` — reference docs, skipped by installer
- `settings.template.json` — installed as target repo's `.claude/settings.json`

Exact exclusions, mappings, and `user_owned` (never-overwrite) paths live in `manifest.json` at the repo root.

## Skill authoring rules

- Frontmatter `name:` must match the directory name.
- `description:` is what the LLM matches against. Be specific about trigger phrases AND include a **"When NOT to Use"** section naming the skills this one should defer to. Overlapping descriptions across skills are the #1 cause of wrong-skill-triggering.
- Worker roles nest **inside the skill package** (e.g. `<skill>/agents/*.md`), not as top-level peers — Claude's model is skill-centric (see repo `README.md` § "Platform modeling note").
- New or renamed skills should also be considered in `codex/`, `copilot/`, and `kimi/`. Keep the four trees in parity.

## Diagnosing "my skill didn't trigger"

The skill is almost always installed; it loses the description match. Workflow:

1. Confirm the skill exists in the harness: `ls ~/repos/skills-test-harness/claude-test/.claude/skills/<name>`.
2. Read its `description:` field. Compare against the user's phrasing.
3. Identify the competing skill. Tighten THIS skill's description; add a "When NOT to Use" line naming the competitor.
4. Re-sync to the harness and re-test in a fresh session — description changes don't take effect mid-session.

`ba-*` skills are for business analysis (problem → stakeholders → current state → requirements → validation → solution). They should never trigger on PRD-to-app/build requests. If they do, that's a description-overlap bug to fix here.

## Dev flow → which skill fires when

For a typical "I have a PRD, build the app" flow, the correct chain is:

```
vague intent → goal → prd-validate → execute-prd (or writing-plans) → execute-plan (or executing-plans) → checkpoint → security-review/review
```

`/goal` sits before PRD work: it validates that the intent is outcome-shaped (not solution-shaped) before requirements are written. Skip it when the problem statement is already clear.

The custom skills here cluster at the quality-gate end of that chain (`checkpoint`, `review-*`, `simplify`). The `ba-*` family is a parallel, non-dev workflow that produces specs; it does not consume them.

## Workflow

- **Branch before any non-trivial change.** `git switch -c <name>` + PR. Never commit multi-file edits directly to `main`.
- After editing: sync to test harness → test in a fresh session → commit on a branch → PR.

## Cross-platform notes

- `kimi/` doesn't duplicate skill bodies — it consumes `claude/` directly via `manifest.json#kimi.skills`. A skill edit here lands in both Claude Code and Kimi installs.
- `codex/` and `copilot/` are independent trees with platform-native formats. Claude skill edits don't auto-port; do it manually.
