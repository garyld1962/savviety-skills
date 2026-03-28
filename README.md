# AI Coding Skills

Cross-platform AI coding skills maintained as a single source of truth and deployed to three environments.

## Platforms

| Platform | Directory | Target Environment | Primary Models |
|----------|-----------|--------------------|----------------|
| [Claude Code](claude/README.md) | `claude/` | `.claude/skills/` | Claude Opus, Sonnet |
| [VS Code / GitHub Copilot](vscode/README.md) | `vscode/` | `.github/` | GPT 5.4, Gemini Pro |
| [Copilot Native](copilot-native/README.md) | `copilot-native/` | `.github/` (Copilot CLI + VS Code) | GPT 5.4, Gemini Pro |

**Claude Code** skills are invoked as `/name` in the CLI. **VS Code** skills are invoked as `#prompt:name` in Copilot Chat. **Copilot Native** is a leaner, platform-first variant of VS Code skills that leans on Copilot built-ins where possible.

## Repository Structure

```
skills/
├── claude/                # Claude Code skills
│   ├── plan/              #   Each skill is a directory with SKILL.md
│   ├── code-review/       #   Some skills have sub-files (specialists, foundations)
│   └── ...
├── vscode/                # VS Code / GitHub Copilot
│   ├── prompts/           #   Copilot Chat commands (#prompt:name)
│   ├── agents/            #   Autonomous agent definitions
│   ├── skills/            #   Reusable domain knowledge
│   └── instructions/      #   Auto-applied rules by file pattern
├── copilot-native/        # Copilot-first workspace
│   ├── prompts/           #   Thinner prompts that lean on built-ins
│   ├── agents/            #   Narrow specialist agents
│   ├── skills/            #   Domain knowledge
│   └── instructions/      #   Auto-applied rules
├── templates/             # Copy-once local file templates
│   ├── CLAUDE.local.md    #   Personal Claude Code overrides
│   ├── blazorstack/       #   Scaffold template
│   └── ts-monorepo/       #   Scaffold template
├── archives/              # Original source zips and snapshots
├── MAPPING.md             # Cross-platform skill mapping reference
└── deploy.sh              # Deploy script (copies to consumption points)
```

## Deployment

```bash
# From any project directory:
deploy-skills              # Interactive — asks claude/vscode/both
deploy-skills both         # Deploy everything
deploy-skills --dry-run    # Preview without copying
```

The `deploy-skills` CLI is installed at `~/.local/bin/deploy-skills`. It copies shared skills to the current project and protects local/project-specific files from being overwritten.

The legacy `deploy.sh` script in this repo copies to hardcoded project paths.

## Shared vs Local Convention

Every deployment target separates **shared** (overwritten on sync) from **local** (never overwritten):

| Layer | Claude Code | VS Code / Copilot Native |
|-------|-------------|--------------------------|
| Shared | `.claude/skills/<name>/` | `.github/prompts/<category>/`, `.github/skills/<name>/` |
| Project | `.claude/skills/_project/` | `.github/prompts/project/`, `.github/skills/project-<name>/` |
| Personal | `CLAUDE.local.md` | `.github/instructions/personal.instructions.md`, `.github/prompts/local/` |

## Cross-Platform Mapping

See [MAPPING.md](MAPPING.md) for the complete mapping between Claude Code, VS Code, and Copilot Native skill equivalents, including sync status.

## Adding Skills

Each platform README documents how to add new skills. The general pattern:

1. Add the skill in the appropriate platform directory
2. Run `deploy-skills` from your project to pick it up
3. Update [MAPPING.md](MAPPING.md) if the skill has cross-platform equivalents
4. Test in the target environment
