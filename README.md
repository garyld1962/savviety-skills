# Skills

Cross-platform AI coding skills for **Claude Code** and **VS Code / GitHub Copilot**. One source of truth, deployed to both environments.

## What's In Here

```
skills/
├── claude/          # Claude Code skills (.claude/skills/)
├── vscode/          # VS Code / GitHub Copilot skills (.github/)
├── deploy.sh        # Deploy to consumption points
├── MAPPING.md       # Cross-platform skill mapping
└── archives/        # Snapshots
```

## Two Skill Sets, One Repo

| Platform | Location | Format | Invoked With |
|----------|----------|--------|-------------|
| **Claude Code** | `claude/<name>/SKILL.md` | Skill with frontmatter | `/name` in Claude Code CLI |
| **VS Code / Copilot** | `vscode/prompts/<category>/<name>.prompt.md` | Prompt with YAML frontmatter | `#prompt:name` in Copilot Chat |

Skills are authored for their target platform but kept in sync where concepts overlap. See [MAPPING.md](MAPPING.md) for the full cross-reference.

---

## Claude Code Skills

Skills for the Claude Code CLI. Deployed to `.claude/skills/` in each project.

### Dev Workflow

| Skill | Purpose |
|-------|---------|
| `/plan` | Create an implementation plan from requirements (supports `--ado` and `--linear`) |
| `/execute-plan` | Execute a plan file end-to-end with per-task build/test cycles |
| `/checkpoint` | Quality gate: lint, build, tests for changed packages |
| `/code-review` | Multi-specialist review with structured findings and verdict |
| `/pr` | Create a PR from current branch |
| `/teams` | Dispatch parallel agent teams for large implementations |
| `/simplify` | Auto-refactoring pass (reuse, quality, efficiency agents) |
| `/hotfix` | Emergency fix workflow |
| `/triage` | Bug triage and priority assessment |
| `/changelog` | Generate changelog from commits |
| `/work-item` | Fetch ADO or Linear work items |
| `/sync-main` | Rebase current branch on main safely |
| `/test-plan` | Generate a test plan with multi-analyst coverage |
| `/k8s-deploy-verify` | Post-deploy Kubernetes health checks |
| `/dependency-audit` | Audit dependencies for vulnerabilities and updates |
| `/migration-guide` | Generate migration guide for breaking changes |

### Review

| Skill | Purpose |
|-------|---------|
| `/review-gauntlet` | Meta-review: challenge a code review's findings |
| `/ba-adversarial-review` | Adversarial review of BA deliverables |
| `/skill-audit` | Audit skill quality and coverage |

### Code Review System

The `/code-review` skill uses a multi-specialist orchestrator with these domain specialists:

| Specialist | Domain |
|-----------|--------|
| `typescript-quality` | Type safety, strict mode, imports |
| `api-patterns` | Service patterns, error handling, validation |
| `ui-design-compliance` | React patterns, accessibility, design |
| `security` | Secrets, injection, auth, K8s manifests |
| `test-quality` | Coverage gaps, behavior testing, isolation |
| `postgres` | Migration safety, query patterns, indexing |

---

## VS Code / GitHub Copilot Skills

See the dedicated [VS Code Skills README](vscode/README.md) for full details, including usage examples and the complete prompt catalog.

---

## Deployment

```bash
./deploy.sh              # Deploy everything
./deploy.sh claude       # Claude skills only
./deploy.sh vscode       # VS Code skills only
./deploy.sh --dry-run    # Preview what would be copied
```

The script copies skills to their consumption points:
- **Claude** → `~/.claude/skills/` or each project's `.claude/skills/`
- **VS Code** → each project's `.github/` directory

Project-specific skills in `_project/` directories are never overwritten.

## Maintenance

1. Edit skills in this repo (`claude/` or `vscode/`)
2. Run `./deploy.sh`
3. Update [MAPPING.md](MAPPING.md) if adding or changing skills
4. Test in the target environment
