# Kimi Code CLI Assets

Kimi-native source assets for Savviety workflows.

## Layout

```
kimi/
├── kimi.plugin.json      # Native Kimi plugin manifest
├── skills/               # Generated from claude/ by bin/build-kimi-plugin
├── commands/             # Plugin slash commands (e.g. /savviety-workflows:review)
├── hooks/                # Kimi-aware hook adapters for install-scan / pr-guardrail / journal
├── agents/               # Custom agent YAML files (empty by default)
└── templates/            # Starter AGENTS.md and config.toml
```

## Two install paths

### 1. Plugin install (recommended for individual users)

Installs skills, slash commands, and session-start guidance at user scope:

```
/plugins install https://github.com/garyld1962/savviety-skills
```

After install, run `/reload` or start a new session. Then use:

- `/savviety-workflows:review` — run a domain-based code review
- `/savviety-workflows:checkpoint` — run the quality gate
- `/savviety-workflows:ship` — ship the current branch
- `/savviety-workflows:status` — show repo state
- `/skill:gh-readiness` — verify GitHub CLI auth before PR/issue workflows
- `/skill:<name>` — invoke any full skill body (e.g. `/skill:domain-review`)

Plugin install does **not** include lifecycle hooks, because Kimi plugins run hooks from the per-user plugin root and cannot reliably reference project-level scripts. Use path 2 for hooks.

### 2. Project install (recommended for teams)

Seeds a target repo with project-level skills, AGENTS.md, config.toml, and hook wiring:

```
# From the source repo
bin/build-kimi-plugin
cli/skill.sh --kimi --init <target>
```

This deploys:

1. `kimi/skills/` → `<target>/.kimi/skills/` (native frontmatter)
2. `kimi/commands/` → `<target>/.kimi/commands/`
3. `kimi/kimi.plugin.json` → `<target>/.kimi/kimi.plugin.json`
4. `kimi/hooks/` → `<target>/.kimi/hooks/`
5. `claude/install-scan/` → `<target>/.kimi/install-scan/`
6. `kimi/templates/AGENTS.starter.md` → `<target>/AGENTS.md`
7. `kimi/templates/config.toml` → `<target>/.kimi/config.toml`

Run `bin/build-kimi-plugin` before `--init` or `--update` so `kimi/skills/` is in sync with `claude/`.

## Why a plugin instead of just `.claude/skills/`?

Kimi Code CLI v1.39+ auto-discovers `.claude/skills/` when `merge_all_available_skills = true`, so the original 2026-05-05 port relied on that to avoid duplication. The plugin adds Kimi-native features that do not auto-port:

- `type: flow` skills with Mermaid workflow support
- `whenToUse` and `arguments` frontmatter for better auto-invocation
- Plugin slash commands (`/savviety-workflows:<command>`)
- `sessionStart.skill` loading

Skill prose remains single-sourced in `claude/` and generated into `kimi/skills/` by `bin/build-kimi-plugin`.

## Regenerating `kimi/skills/`

```
bin/build-kimi-plugin
```

Run `--check` in CI to fail when the generated tree is stale:

```
bin/build-kimi-plugin --check
```

## Authoring rules

- **Skill bodies:** edit in `claude/<skill>/SKILL.md`. Do not hand-edit `kimi/skills/` — it is generated.
- **Slash commands:** add/edit `.md` files in `kimi/commands/`.
- **Hook adapters:** edit scripts in `kimi/hooks/`.
- **Plugin manifest:** edit `kimi/kimi.plugin.json`.
- **Custom agents:** add `<name>.yaml` + `<name>-system.md` to `kimi/agents/` only when the system prompt is fully specified (no runtime placeholders).

## User-facing differences from Claude

| Concern | Claude | Kimi |
|---|---|---|
| Slash invocation | `/domain-review` | `/skill:domain-review` or `/savviety-workflows:review` |
| Project instruction file | `CLAUDE.md` | `AGENTS.md` (auto-injected as `${KIMI_AGENTS_MD}`) |
| Personal overlay | `CLAUDE.local.md` | `~/.kimi-code/AGENTS.md` |
| Subagent dispatch | `Agent` tool, `subagent_type: general-purpose / Explore / Plan` | `Agent` tool, `subagent_type: coder / explore / plan` |
| Permission gating | `.claude/settings.local.json` | `.kimi/config.toml` |
| Discovery scopes | implicit user vs project | `### Project` / `### User` / `### Extra` / `### Built-in` headings |
| Plugin install | N/A | `/plugins install <url>` |

## Native Kimi features used

- **Agent Skills** with `name`, `description`, `type`, `whenToUse`, `arguments`
- **Flow skills** (`type: flow`) for multi-phase pipelines: `kickoff`, `execute-plan`, `execute-prd`, `triage`, `hotfix`, `test-plan`, `checkpoint`, `pr`, `ship`
- **Plugin slash commands** for common manual invocations
- **Inline hooks** (`[[hooks]]` in `config.toml`) wired through Kimi-aware adapters
- **`sessionStart.skill`** loads `skill-help` at session start

## GitHub CLI integration

GitHub-dependent skills (`/pr`, `/ship`, `/hotfix`, `/issue-slices`, `/bug-session`, `/changelog`) use the `gh` CLI rather than an MCP server. This keeps the dependency simple and matches the existing Claude workflow.

- Run `/skill:gh-readiness` before a GitHub-dependent workflow to verify `gh` is installed, authenticated, and can reach the API.
- The shipped `[[hooks]]` include `gh-auth-guard`, which blocks `gh pr create`, `gh issue create`, and `gh release create` when `gh` is missing or not authenticated.
- Slash commands for `review`, `status`, and `ship` show the preferred `gh --json` + `jq` patterns.

## Suggested native add-ins

See `docs/kimi-port-plan.md` § "Missing plugins / native addins" for the full list. The highest-value additions are:

1. **GitHub MCP server** — optional alternative to `gh` CLI for richer typed tooling; current implementation uses `gh`. (see GitHub CLI integration above)
2. **Kubernetes MCP server** — lets `/k8s-verify` query cluster state without shelling out.
3. **OSV / supply-chain MCP server** — powers `/dep-audit` with CVE and maintainer-risk data.
4. **Kimi Datasource plugin** — market/domain research for `/thesis`, `/what-is-it-about`, and `/prd-validate`.
5. **Kimi `/remember`** — replace the deprecated handoff pattern for session continuity across long `/execute-plan` runs.
6. **Kimi `/goal` mode** — run `/kickoff`, `/execute-prd`, and `/execute-plan` as autonomous goals with explicit completion criteria.
