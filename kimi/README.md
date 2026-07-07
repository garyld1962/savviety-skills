# Kimi Code CLI Assets

Kimi-native source assets for Savviety workflows. The skill bodies themselves live under `claude/` — Kimi auto-discovers `.claude/skills/` (since v1.39, 2026-04-24), so this directory only contains what cannot be shared with Claude.

## Layout

- `agents/` — custom agent YAML files (Kimi v1 agent schema). Empty by default; see `agents/README.md` for when to add one.
- `templates/` — starter `AGENTS.md` and `config.toml` for downstream repos. The `config.toml` embeds Kimi's hook configuration inline as `[[hooks]]` blocks (Kimi does not use a separate `hooks.json`).

Skills are NOT mirrored here — the deploy manifest ships `claude/<skill>/SKILL.md` into both `.claude/skills/` and `.kimi/skills/` so Kimi sees them under the `### User` / `### Project` scope headings in its system prompt. Hook script bodies are also single-sourced from `claude/infra/` and deployed by the manifest into `.kimi/install-scan/`, `.kimi/journal/`, and `.kimi/pr-guardrail/`.

## Why no skills/ directory

Kimi Code CLI's discovery model (v1.39+, `merge_all_available_skills = true` by default) merges every brand directory it finds — `.kimi/skills/`, `.claude/skills/`, `.codex/skills/` — at both project and user scope, with priority `kimi > claude > codex`. So a single source-of-truth in `claude/` is sufficient for all three CLIs to see the same skill set.

If a Kimi-only skill ever needs to ship (e.g., a Kimi-specific flow skill with embedded Mermaid), add `kimi/skills/<name>/SKILL.md` and a corresponding manifest tree.

## User-facing differences from Claude

| Concern | Claude | Kimi |
|---|---|---|
| Slash invocation | `/domain-review` | `/skill:domain-review` (or `/flow:<name>` for type=flow skills) |
| Project instruction file | `CLAUDE.md` | `AGENTS.md` (auto-injected as `${KIMI_AGENTS_MD}`) |
| Personal overlay | `CLAUDE.local.md` | `~/.kimi/AGENTS.md` (user-level) |
| Subagent dispatch | `Agent` tool, `subagent_type: general-purpose / Explore / Plan` | `Agent` tool, `subagent_type: coder / explore / plan` |
| Permission gating | `.claude/settings.local.json` | `.kimi/config.toml` |
| Discovery scopes | implicit user vs project | `### Project` / `### User` / `### Extra` / `### Built-in` headings, priority Project > User > Extra > Built-in |

## Authoring Rules

- Skill bodies belong in `claude/`, not here. This directory is for Kimi-only assets.
- When porting a Claude agent to Kimi, ship a `name.yaml` (Kimi v1 agent schema) plus a sibling `name-system.md` with the system prompt body.
- Keep agent YAML thin: prefer `extend: default` over redefining tools, and stash long prose in `name-system.md`.
- Subagent dispatch should target Kimi's built-in `coder` / `explore` / `plan` types when the role matches; only define a custom subagent when the role is genuinely different.
- AGENTS.md is shared with Codex. Keep it CLI-neutral; do not reference Kimi-specific behavior.

## Install

Use the repo installer:

```
cli/skill.sh --kimi --init   <target>
cli/skill.sh --kimi --update <target>
```

Behind the scenes this:
1. Rsyncs `claude/<skill>/SKILL.md` trees into `<target>/.kimi/skills/`
2. Rsyncs `kimi/agents/` and `kimi/templates/` into `<target>/.kimi/`
3. Rsyncs hook script bundles from `claude/infra/{install-scan,journal,pr-guardrail}/` into `<target>/.kimi/{install-scan,journal,pr-guardrail}/`
4. Seeds `AGENTS.md` from `kimi/templates/AGENTS.starter.md` if absent
5. Seeds `.kimi/config.toml` (containing inline `[[hooks]]` blocks) if absent

The shipped `config.toml` keeps all `[[hooks]]` blocks commented out by default — uncomment after verifying the corresponding shell script behaves correctly under Kimi's hook stdin format (the scripts were authored for Claude Code's `$CLAUDE_PROJECT_DIR` model).
