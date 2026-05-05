# AI Coding Skills

Cross-platform AI coding skills maintained across two canonical systems.

## Platforms

| Platform | Directory | Target Environment | Primary Models |
|----------|-----------|--------------------|----------------|
| [Claude Code](claude/README.md) | `claude/` | `.claude/skills/` | Claude Opus, Sonnet |
| [Copilot Native](copilot-native/README.md) | `copilot-native/` | `.github/` (Copilot CLI + VS Code) | GPT 5.4, Gemini Pro |

**Claude Code** workflows are primarily modeled as `/name` skills. When Claude
needs worker roles, they usually live **inside the skill package** as nested
sub-files or subskills rather than as a first-class top-level agent asset type.
**Copilot Native** uses `/<prompt-name>` prompts plus first-class `@agent-name`
agents.

## Repository Structure

```
	skills/
	├── claude/                # Claude Code skills
	│   ├── execute-plan/      #   User-invokable skill directories
	│   ├── code-review/       #   Composite skill with private resources
	│   ├── configure/         #   Template-filling skill + registry
	│   ├── _internal/         #   Internal callable contracts and rubrics
	│   ├── infra/             #   Hook and utility script sources
	│   └── ...
├── copilot-native/        # Copilot-first workspace
│   ├── prompts/           #   Thinner prompts that lean on built-ins
│   ├── agents/            #   Narrow specialist agents
│   ├── skills/            #   Domain knowledge
│   ├── instructions/      #   Auto-applied rules
│   └── templates/         #   Blank config templates for user setup
├── templates/             # Project scaffold templates
│   ├── CLAUDE.local.md    #   Personal Claude Code overrides
│   ├── blazorstack/       #   .NET scaffold template
│   └── ts-monorepo/       #   TypeScript scaffold template
├── archives/              # Deprecated assets (vscode/, MAPPING.md, deploy.sh)
├── docs/                  # Design and planning docs
└── COPILOT-NATIVE-PARITY.md  # Port plan and decision log
```

## Deployment

Deployment into a target repository is handled by `bin/repo-skills` using
`manifest.json`. The legacy `deploy.sh` script has been archived.

For Claude Code, user-facing skill directories and `_internal/` map into
`.claude/skills/`, while runtime project files such as `.claude/settings.json`
and hook utilities live at `.claude/` root. `claude/infra/` is source for those
hook utilities, not a skill namespace. `claude/README.md`,
`claude/MODEL-POLICY.md`, and `claude/SESSION-CONTEXT.md` are source/reference
docs, not files to drop into `.claude/skills/`.

## Shared vs Local Convention

Every deployment target separates **shared** (overwritten on sync) from **local** (never overwritten):

| Layer | Claude Code | Copilot Native |
|-------|-------------|----------------|
| Shared | `.claude/skills/<name>/` | `.github/prompts/<category>/`, `.github/skills/<name>/` |
| Project | `.claude/skills/_project/` | `.github/prompts/project/`, `.github/skills/project-<name>/` |
| Personal | `CLAUDE.local.md` | `.github/instructions/personal.instructions.md`, `.github/prompts/local/` |

## Architecture Principles

1. **Two canonical systems.** Claude Code (`claude/`) and Copilot Native (`copilot-native/`).
2. **Environment-neutral.** Skills never hardcode shells, hostnames, or project names. Variable data lives in user-editable config templates.
3. **Config via `/configure`.** Skills that need user-specific data ship blank templates. Users fill them in via `/configure <target>` or by hand.
4. **Pre-flight checks.** Config-dependent skills halt with actionable messages if config is missing.
5. **Internal contracts are hidden from normal help.** Knowledge rubrics and reusable contracts live in `claude/_internal/` with `user-invocable: false`; user-facing skills call them by contract.

## Platform modeling note

The two platforms do **not** represent worker roles the same way:

- **Claude Code** usually treats the top-level deployable unit as the
  **skill**. Worker roles are often nested inside the skill package (for
  example `execute-plan/agents/*.md`) or represented as subskills/specialists inside
  the same workflow tree.
- **Copilot Native** has a first-class top-level **agent** asset layer under
  `copilot-native/agents/`.

So a one-for-one "every Copilot agent must become a top-level Claude agent"
port is too literal. The parity question is whether the worker role exists in
the Claude workflow, not whether it exists as a top-level peer directory.

## Repository-level Copilot instructions

This repo now has a real project instruction file at
`.github/copilot-instructions.md`.

That file is the top-level source of truth when using Copilot in this
repository, including when authoring the assets under `copilot-native/`. The
files inside `copilot-native/` are source templates for downstream repos, not
the governing instruction layer for this repository itself.

## Adding Skills

1. Add the skill in the appropriate platform directory
2. If the skill needs user config, add a `config.template.md` and a registry entry in `claude/configure/registry.md`
3. Embed the pre-flight check pattern if the skill depends on config
4. Test in the target environment
