# AI Coding Skills

[![CI](https://github.com/garyld1962/savviety-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/garyld1962/savviety-skills/actions/workflows/ci.yml)

Cross-platform AI coding skills, including an initial Hermes workflow package.

## Platforms

| Platform | Directory | Target Environment | Primary Models |
|----------|-----------|--------------------|----------------|
| [Claude Code](claude/README.md) | `claude/` | `.claude/skills/` | Claude Opus, Sonnet |
| [Copilot](copilot/README.md) | `copilot/` | `.github/` (Copilot CLI + VS Code) | GPT 5.4, Gemini Pro |
| [Codex](codex/README.md) | `codex/` | `.codex/`, `.claude-plugin/marketplace.json`, `AGENTS.md` | GPT-5 Codex family |
| [Kimi](kimi/README.md) | `kimi/` | `.kimi/`, `AGENTS.md` (skills sourced from `claude/`) | Kimi K2.5/K2.6 |
| [Hermes Agent](hermes/README.md) | `hermes/skills/` | `$HERMES_HOME/skills/` (default `~/.hermes/skills/`) | Configured Hermes model |

**Claude Code** workflows are primarily modeled as `/name` skills. When Claude
needs worker roles, they usually live **inside the skill package** as nested
sub-files or subskills rather than as a first-class top-level agent asset type.
**Copilot Native** uses `/<prompt-name>` prompts plus first-class `@agent-name`
agents.
**Codex** uses plugins as the installable distribution unit, `SKILL.md` skills
as reusable workflow packages, `.codex/agents/*.toml` for custom subagents, and
`AGENTS.md` as the project instruction layer.
**Kimi Code CLI** auto-discovers `.claude/skills/` natively (since v1.39, with
`merge_all_available_skills = true` by default), so the `kimi/` tree only ships
Kimi-specific YAML agents, hooks, and an `AGENTS.md` starter — skill bodies
stay single-sourced under `claude/`. Slash invocation differs from Claude:
`/skill:<name>` and `/flow:<name>` instead of `/<name>`.
**Hermes Agent** has a four-skill pilot: `/simplify`, `/validate-plan`,
`/execute-prd`, and `/execute-plan`. Thin Hermes entrypoints use the shared
workflow instructions and validators. It does not yet have the full catalog.

## Repository Structure

```
	skills/
	├── claude/                # Claude Code skills
	│   ├── execute-plan/      #   User-invokable skill directories
	│   ├── domain-review/     #   Composite skill with private resources
	│   ├── configure/         #   Template-filling skill + registry
	│   ├── _internal/         #   Internal callable contracts and rubrics
	│   ├── infra/             #   Hook and utility script sources
	│   └── ...
├── copilot/        # Copilot-first workspace
│   ├── prompts/           #   Thinner prompts that lean on built-ins
│   ├── agents/            #   Narrow specialist agents
│   ├── skills/            #   Domain knowledge
│   ├── instructions/      #   Auto-applied rules
│   └── templates/         #   Blank config templates for user setup
├── codex/                 # Codex-native plugin, skills, agents, hooks, rules
│   ├── plugins/           #   Local Codex plugins
│   ├── agents/            #   Project-scoped custom agent TOML files
│   ├── templates/         #   AGENTS.md/config/hooks/rules starters
│   └── prompts/           #   Documented prompt examples
├── kimi/                  # Kimi Code CLI overlay (skills auto-sourced from claude/)
│   ├── agents/            #   Kimi v1 agent YAML + system-prompt files
│   └── templates/         #   AGENTS.md / config.toml starters (hooks embedded as TOML)
├── templates/             # Project scaffold templates
│   ├── CLAUDE.local.md    #   Personal Claude Code overrides
│   ├── blazorstack/       #   .NET scaffold template
│   └── ts-monorepo/       #   TypeScript scaffold template
├── docs/                  # Design and planning docs
├── hermes/                # Hermes entrypoints and packaged shared contracts
├── install.sh             # Installs the skills command in ~/.local/bin
└── cli/                   # Implementation of skills, driven by manifest.json
```

## Installation

Clone this repository wherever you keep your source code, then run `install.sh`:

```bash
git clone https://github.com/garyld1962/savviety-skills.git
cd savviety-skills
./install.sh
```

The installer creates `~/.local/bin/skills` as a symlink to this checkout's
`cli/skill.sh` and adds `~/.local/bin` to PATH in your shell startup files.
It supports Bash, Zsh (including `ZDOTDIR`), and POSIX login shells (`sh`,
`dash`, `ksh`). Rerunning it does not duplicate the PATH setup or replace an
existing regular file or directory named `skills`.

Open a new terminal after installation. To use the command immediately in the
current terminal, run:

```bash
export PATH="$HOME/.local/bin:$PATH"
skills --help
```

Keep the checkout: the command runs directly from it, so pulling updates also
updates `skills`. If you move the checkout, rerun `./install.sh` from its new
location. `REPO_SKILLS_HOME` remains available to override the source repository.

To repair the command, install missing utilities, and refresh a Claude project:

```bash
./update.sh /path/to/project
```

The target defaults to the current directory and must be a Git repository.
Existing Claude installs are updated; new ones are initialized. Shared hook
registrations are removed from `settings.json`, existing permissions are
preserved, and an existing `settings.local.json` is left untouched.
The script installs `uv`, Python if needed, and these utilities: `ripgrep`,
`fd`, `jq`, `rsync`, `shellcheck`, `ast-grep`, `sd`, `gh`, `gh-axi`, `just`,
`hyperfine`, and `xh`. Installing `gh-axi` requires Node.js 20+ and npm; its
executable is installed into `~/.local/bin` without registering session hooks.
Debian/Ubuntu package installation may require sudo. Failed installations
stop the update and report what is still missing.

For Hermes, use the same utility setup with a profile destination:

```bash
./update.sh --hermes
# Or select a named profile explicitly:
./update.sh --hermes "$HOME/.hermes/profiles/coder"
```

The destination defaults to `HERMES_HOME`, otherwise `~/.hermes`. Hermes
configuration, hooks and unrelated skills are preserved. Updates stop before
overwriting local skill edits. See [Hermes installation and validation](hermes/README.md).

You can also run `bin/install-agentic-tools` separately. It
installs missing `uv` using [Astral's installer](https://docs.astral.sh/uv/reference/installer/),
then configures the tool directory's PATH and installs Python if needed.
Use `bin/install-agentic-tools --check` to report missing prerequisites without
installing anything.

CI runs ShellCheck on the installer scripts. Run the same check locally with:

```bash
shellcheck install.sh update.sh cli/skill.sh bin/install-agentic-tools
```

## Deployment

Deployment into a target repository is handled by `skills` using
`manifest.json`. The legacy `deploy.sh` script has been archived.

For Claude, Copilot, Codex and Kimi, the target must already be a Git repository. Deployment requires Bash, Git,
`jq`, and `rsync` on PATH. Choose your platform:

```bash
skills --claude --init /path/to/project
skills --copilot --init /path/to/project
skills --codex --init /path/to/project
# For Kimi, first run bin/build-kimi-plugin from the source checkout:
skills --kimi --init /path/to/project
```

To refresh an existing install, use `--update` with the same platform flag.
Omit the target path to use the current directory. Run `skills --help` for
all options, including `--dry-run`.

Hermes installs into a profile home and requires Bash and Python 3.9+, without
a Git repository, jq or rsync requirement for the skill copy itself:

```bash
skills --hermes --init --dry-run
skills --hermes --init
skills --hermes --update
```

For Claude Code, user-facing skill directories and `_internal/` map into
`.claude/skills/`, while runtime project files such as `.claude/settings.json`
and hook utilities live at `.claude/` root. `claude/infra/` is source for those
hook utilities, not a skill namespace. `claude/README.md`,
`claude/MODEL-POLICY.md`, and `claude/SESSION-CONTEXT.md` are source/reference
docs, not files to drop into `.claude/skills/`.

The installer refreshes Claude's shared settings without importing template
permissions. Existing permissions in `.claude/settings.json` are preserved;
`.claude/settings.local.json` is created as `{}` only if absent.
The template registers no hooks. Updating an existing install removes the
previous template hooks from `.claude/settings.json`.

## Clear progress updates

PRD, kickoff, and plan execution apply a plain-language pass to assistant-written
updates: what changed, what remains uncertain, why it matters, and the next action
or decision. Detailed reports keep their technical findings and verdicts.

Invoke `/simplify` to re-explain the latest update, or `/simplify <report-path>`
to explain a specific report. Use `$simplify` in Codex and `/skill:simplify` in
Kimi; Copilot also ships a `/simplify` prompt where prompt files are supported.
This skill simplifies explanations, not code. It does not install hooks or
intercept raw output rendered by the host's tools.

## Shared vs Local Convention

Every deployment target separates **shared** (overwritten on sync) from **local** (never overwritten):

| Layer | Claude Code | Copilot Native | Codex | Kimi |
|-------|-------------|----------------|-------|------|
| Shared | `.claude/skills/<name>/` | `.github/prompts/<category>/`, `.github/skills/<name>/` | `.codex/plugins/`, `.codex/agents/`, `.codex/rules/` | `.kimi/skills/<name>/`, `.kimi/agents/` |
| Project | `.claude/skills/_project/` | `.github/prompts/project/`, `.github/skills/project-<name>/` | nested `AGENTS.md`, project `.codex/config.toml` | nested `AGENTS.md`, `.kimi/config.toml` |
| Personal | `CLAUDE.local.md` | `.github/instructions/personal.instructions.md`, `.github/prompts/local/` | user-level `~/.codex/config.toml`, `~/.codex/AGENTS.md` | user-level `~/.kimi/config.toml`, `~/.kimi/AGENTS.md` |

## Architecture Principles

1. **Four canonical systems.** Claude Code (`claude/`), Copilot (`copilot/`), Codex (`codex/`), and Kimi (`kimi/` overlay over `claude/`).
2. **Environment-neutral.** Skills never hardcode shells, hostnames, or project names. Variable data lives in user-editable config templates.
3. **Config via `/configure`.** Skills that need user-specific data ship blank templates. Users fill them in via `/configure <target>` or by hand.
4. **Pre-flight checks.** Config-dependent skills halt with actionable messages if config is missing.
5. **Internal contracts are hidden from normal help.** Knowledge rubrics and reusable contracts live in `claude/_internal/` with `user-invocable: false`; user-facing skills call them by contract.

## Platform modeling note

The platforms do **not** represent worker roles the same way:

- **Claude Code** usually treats the top-level deployable unit as the
  **skill**. Worker roles are often nested inside the skill package (for
  example `execute-plan/agents/*.md`) or represented as subskills/specialists inside
  the same workflow tree.
- **Copilot Native** has a first-class top-level **agent** asset layer under
  `copilot/agents/`.
- **Codex** has project-scoped custom agent TOML files under `.codex/agents/`
  and only spawns subagents when explicitly asked.

So a one-for-one "every Copilot agent must become a top-level Claude agent"
port is too literal. The parity question is whether the worker role exists in
the Claude workflow, not whether it exists as a top-level peer directory.

## Repository-level Copilot instructions

This repo now has a real project instruction file at
`.github/copilot-instructions.md`.

That file is the top-level source of truth when using Copilot in this
repository, including when authoring the assets under `copilot/`. The
files inside `copilot/` are source templates for downstream repos, not
the governing instruction layer for this repository itself.

## Adding Skills

1. Add the skill in the appropriate platform directory
2. If the skill needs user config, add a `config.template.md` and a registry entry in `claude/configure/registry.md`
3. Embed the pre-flight check pattern if the skill depends on config
4. Test in the target environment
