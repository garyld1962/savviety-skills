# AI Coding Skills

Cross-platform AI coding skills maintained across two canonical systems.

## Platforms

| Platform | Directory | Target Environment | Primary Models |
|----------|-----------|--------------------|----------------|
| [Claude Code](claude/README.md) | `claude/` | `.claude/skills/` | Claude Opus, Sonnet |
| [Copilot Native](copilot-native/README.md) | `copilot-native/` | `.github/` (Copilot CLI + VS Code) | GPT 5.4, Gemini Pro |

**Claude Code** skills are invoked as `/name` in the CLI. **Copilot Native** skills are invoked as `/<prompt-name>` in Copilot CLI or VS Code Copilot Chat, with agents available via `@<agent-name>`.

## Repository Structure

```
skills/
├── claude/                # Claude Code skills
│   ├── plan/              #   Each skill is a directory with SKILL.md
│   ├── execute-workflow/  #   Some skills have templates and sub-files
│   ├── configure/         #   Template-filling skill + registry
│   ├── _rubrics/          #   Knowledge rubrics (not user-invokable)
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

Deployment is handled by the [skill-factory](https://github.com/garyld1962/skill-factory) compile+publish pipeline. The legacy `deploy.sh` script has been archived.

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
5. **Rubrics are reference-only.** Knowledge rubrics live in `claude/_rubrics/` and are referenced by user-invokable skills, not invoked directly.

## Adding Skills

1. Add the skill in the appropriate platform directory
2. If the skill needs user config, add a `config.template.md` and a registry entry in `claude/configure/registry.md`
3. Embed the pre-flight check pattern if the skill depends on config
4. Test in the target environment
