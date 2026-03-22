# Skills

Cross-platform AI coding skills for **Claude Code** and **VS Code / GitHub Copilot**. One source of truth, deployed to both environments.

## Quick Start

```bash
# From any project directory:
deploy-skills              # Interactive — asks claude/vscode/both
deploy-skills both         # Deploy everything
deploy-skills --dry-run    # Preview without copying
```

The script is installed at `~/.local/bin/deploy-skills` and copies common skills into the current directory.

## Repository Structure

```
skills/
├── claude/              # Claude Code skills → .claude/skills/
├── vscode/              # VS Code / GitHub Copilot → .github/
│   ├── prompts/         #   Copilot Chat prompts (#prompt:name)
│   ├── agents/          #   Autonomous agent definitions
│   ├── skills/          #   Reusable domain knowledge
│   └── instructions/    #   Auto-applied rules by file pattern
├── templates/           # Copy-once local file templates
│   └── CLAUDE.local.md  #   Personal Claude Code overrides
├── MAPPING.md           # Cross-platform skill mapping reference
└── deploy.sh            # Legacy deploy (per-project hardcoded paths)
```

## How It Works

### Two Channels: Shared and Local

Every file managed by `deploy-skills` falls into one of two categories:

| Channel | Behavior | Purpose |
|---------|----------|---------|
| **Shared** | Overwritten on every run | Common skills, prompts, agents, instructions |
| **Local** | Created once, never overwritten | Personal preferences, project-specific config |

### What Goes Where

**Claude Code** target (`deploy-skills claude`):

```
your-project/
├── CLAUDE.md                    # Your project config (you maintain this)
├── CLAUDE.local.md              # LOCAL — personal overrides (copy-once)
└── .claude/
    └── skills/
        ├── plan/SKILL.md        # SHARED — overwritten each deploy
        ├── code-review/         # SHARED — overwritten each deploy
        │   ├── SKILL.md
        │   ├── foundations/
        │   └── specialists/
        └── _project/            # LOCAL — never touched by deploy-skills
            └── my-custom/SKILL.md
```

**VS Code** target (`deploy-skills vscode`):

```
your-project/
└── .github/
    ├── copilot-instructions.md          # LOCAL — project conventions (copy-once)
    ├── prompts/
    │   ├── dev/plan.prompt.md           # SHARED
    │   ├── review/code-review.prompt.md # SHARED
    │   └── _project/                    # LOCAL — never touched
    ├── agents/
    │   ├── security.agent.md            # SHARED
    │   └── _project/                    # LOCAL — never touched
    ├── skills/
    │   ├── typescript-quality/SKILL.md  # SHARED
    │   └── _project/                    # LOCAL — never touched
    └── instructions/
        ├── code-generation.instructions.md  # SHARED
        ├── wsl.instructions.md              # SHARED
        └── personal.instructions.md         # LOCAL — your preferences (copy-once)
```

### Local Files

These files are created as starter templates on first run but **never overwritten** on subsequent runs:

| File | Purpose | Platform |
|------|---------|----------|
| `CLAUDE.local.md` | Personal Claude Code preferences and focus areas | Claude Code |
| `.github/copilot-instructions.md` | Project tech stack, build commands, conventions | VS Code |
| `.github/instructions/personal.instructions.md` | Personal coding preferences (auto-applied to all files) | VS Code |

To force-refresh local templates (replaces them with the latest version from this repo):

```bash
deploy-skills both --update-local
```

### _project/ Directories

For project-specific skills that don't belong in the shared repo, create a `_project/` subdirectory:

```bash
# Claude Code
mkdir -p .claude/skills/_project/my-domain
echo "---\nname: my-domain\n---\n# My Domain Knowledge" > .claude/skills/_project/my-domain/SKILL.md

# VS Code
mkdir -p .github/prompts/_project
# Add your custom prompts here
```

`deploy-skills` never reads, writes, or deletes anything inside `_project/` directories.

### CLAUDE.local.md

Claude Code loads files referenced with `@` includes in CLAUDE.md. To enable local overrides, add this line to your project's `CLAUDE.md`:

```markdown
@CLAUDE.local.md
```

Claude Code will include the file if it exists and silently skip it if it doesn't. The `deploy-skills` script creates a starter template and warns you if the `@` include is missing.

### Git Exclude Strategy

Personal local files should not be committed to the repository. Instead of adding them to `.gitignore` (which affects all developers), `deploy-skills` appends rules to `.git/info/exclude` — the per-developer gitignore that is never committed.

Rules added automatically:

```gitignore
CLAUDE.local.md
.github/instructions/personal.instructions.md
.github/*/_project/
.claude/skills/_project/
```

This keeps the repo's `.gitignore` clean and avoids teaching every teammate about your personal files.

## Command Reference

```bash
deploy-skills                    # Interactive menu
deploy-skills claude             # Claude Code skills only
deploy-skills vscode             # VS Code / GitHub Copilot skills only
deploy-skills both               # Everything

deploy-skills both --dry-run     # Preview without copying
deploy-skills both --update-local  # Force-refresh local templates
deploy-skills --help             # Show help
```

## Skill Catalog

### Claude Code Skills

Invoked as `/name` in the Claude Code CLI.

#### Dev Workflow

| Skill | Purpose |
|-------|---------|
| `/plan` | Create an implementation plan from requirements |
| `/execute-plan` | Execute a plan file with per-task build/test cycles |
| `/checkpoint` | Quality gate: lint, build, tests for changed packages |
| `/code-review` | Multi-specialist review with structured findings |
| `/pr` | Create a PR from current branch |
| `/teams` | Dispatch parallel agent teams for large implementations |
| `/hotfix` | Emergency fix workflow |
| `/triage` | Bug triage and priority assessment |
| `/changelog` | Generate changelog from commits |
| `/work-item` | Fetch ADO or Linear work items |
| `/sync-main` | Rebase current branch on main safely |
| `/test-plan` | Generate a test plan with multi-analyst coverage |
| `/k8s-deploy-verify` | Post-deploy Kubernetes health checks |
| `/dependency-audit` | Audit dependencies for vulnerabilities and updates |
| `/migration-guide` | Generate migration guide for breaking changes |
| `/acceptance` | Acceptance criteria validation |

#### Review

| Skill | Purpose |
|-------|---------|
| `/review-gauntlet` | Meta-review: challenge a code review's findings |
| `/ba-adversarial-review` | Adversarial review of BA deliverables |
| `/skill-audit` | Audit skill quality and coverage |

### VS Code / GitHub Copilot Skills

See the dedicated [VS Code Skills README](vscode/README.md) for the full prompt catalog, agent list, and usage examples.

### Cross-Platform Mapping

See [MAPPING.md](MAPPING.md) for the complete mapping between Claude Code and VS Code skill equivalents, including sync status.

## VS Code Instructions

Auto-applied rules that activate based on file patterns:

| Instruction | Applies To | Purpose |
|-------------|-----------|---------|
| `code-generation` | `*.{ts,tsx,cs,js,jsx}` | Read-before-write, import verification, pattern matching |
| `wsl` | `*.{sh,bash,yml,yaml,json,Dockerfile,...}` | WSL2/Linux execution rules, run.sh pattern, path handling |
| `docx-processing` | `*.docx` | Word document handling |
| `pdf-processing` | `*.pdf` | PDF extraction and manipulation |
| `pdf-forms` | PDF forms | PDF form filling |
| `pptx-processing` | `*.pptx` | PowerPoint handling |
| `xlsx-processing` | `*.xlsx` | Spreadsheet handling |
| `personal` | `**/*` (all files) | Your personal preferences (copy-once, not overwritten) |

## Maintenance

1. Edit skills in this repo (`claude/`, `vscode/`, or `templates/`)
2. Run `deploy-skills both` from each project directory (or use the legacy `./deploy.sh`)
3. Update [MAPPING.md](MAPPING.md) if adding or changing skills
4. Test in the target environment

### Adding a New Shared Skill

**Claude Code:**
```bash
mkdir -p claude/my-skill
cat > claude/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: "What it does"
---

# My Skill

Instructions here.
EOF
```

**VS Code prompt:**
```bash
cat > vscode/prompts/dev/my-skill.prompt.md << 'EOF'
---
description: "What it does"
agent: 'agent'
tools: ['editFiles', 'runTerminalCommand']
---

# My Skill

Instructions here.

## CRITICAL: Do Not Guess
- Detect X from the project, do not assume
EOF
```

Then run `deploy-skills both` from your project to pick it up.

### Adding a New Local/Copy-Once File

1. Add the template to `templates/` (for root-level files) or the appropriate `vscode/` subdirectory
2. Update `deploy-skills` to use `copy_local` instead of `cp` for the new file
3. Add a git exclude rule in the `setup_git_excludes` function
