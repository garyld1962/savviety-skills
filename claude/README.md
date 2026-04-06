# Claude Code Skills

Skills for **Claude Code** (Anthropic's CLI). Invoked as `/name` in conversations.

## Setup

Deploy to a project with:

```bash
deploy-skills claude       # From the target project directory
```

This copies skills into the project's `.claude/skills/` directory.

## Skill Catalog

### Dev Workflow

| Skill | Invocation | Purpose |
|-------|------------|---------|
| plan | `/plan` | Create an implementation plan from requirements |
| execute-plan | `/execute-plan` | Execute a plan file with per-task build/test cycles |
| checkpoint | `/checkpoint` | Quality gate: lint, build, tests for changed packages |
| code-review | `/code-review` | Multi-specialist review with structured findings |
| pr | `/pr` | Create a PR from current branch |
| teams | `/teams` | Dispatch parallel agent teams for large implementations |
| hotfix | `/hotfix` | Emergency fix workflow |
| triage | `/triage` | Bug triage and priority assessment |
| changelog | `/changelog` | Generate changelog from commits |
| work-item | `/work-item` | Fetch ADO or Linear work items |
| sync-main | `/sync-main` | Rebase current branch on main safely |
| test-plan | `/test-plan` | Generate a test plan with multi-analyst coverage |
| k8s-verify | `/k8s-verify` | Post-deploy Kubernetes health checks |
| dep-audit | `/dep-audit` | Audit dependencies for vulnerabilities and updates |
| dep-migrate | `/dep-migrate` | Generate migration guide for breaking changes |
| prd-acceptance | `/prd-acceptance` | Post-implementation acceptance criteria validation |

### Review

| Skill | Invocation | Purpose |
|-------|------------|---------|
| review-adversarial | `/review-adversarial` | Cross-model adversarial review using an opposing CLI/model |
| review-api | `/review-api` | Quick API/service pattern compliance check |
| review-db | `/review-db` | Quick database/schema pattern compliance check |
| review-design | `/review-design` | Quick design system and UI compliance check |
| review-tests | `/review-tests` | Quick test quality and coverage pattern check |
| review-gauntlet | `/review-gauntlet` | Meta-review: challenge a code review's findings |
| ba-review-adversarial | `/ba-review-adversarial` | Adversarial review of BA deliverables |
| skill-audit | `/skill-audit` | Audit skill quality and coverage |

### Technology / Reference

| Skill | Invocation | Purpose |
|-------|------------|---------|
| agent-browser | `/agent-browser` | Browser automation and page interaction workflow |
| next-best-practices | `/next-best-practices` | Next.js architecture and implementation guidance |
| typescript-advanced-types | `/typescript-advanced-types` | Advanced TypeScript type-system reference |
| vercel-composition-patterns | `/vercel-composition-patterns` | React composition patterns and tradeoffs |
| vercel-react-best-practices | `/vercel-react-best-practices` | React and Next.js performance and architecture guidance |

### Utility

| Skill | Invocation | Purpose |
|-------|------------|---------|
| find-skills | `/find-skills` | Discover installable ecosystem skills for a given need |

## Multi-File Skills

Some skills have sub-files for specialists, analysts, or shared foundations:

```
code-review/
├── SKILL.md                           # Orchestrator
├── foundations/                        # Shared schemas, rubrics, templates
│   ├── finding-schema.md
│   ├── severity.md
│   └── report-template.md
├── specialists/                       # Domain-specific reviewers
│   ├── typescript-quality/SKILL.md
│   ├── security/SKILL.md
│   └── ...
└── report-writer/SKILL.md             # Report formatter

test-plan/
├── SKILL.md                           # Orchestrator
├── foundations/                        # Shared schemas, rubrics
├── analysts/                          # Domain-specific analysts
└── test-writer/SKILL.md               # Test case writer

teams/
├── SKILL.md                           # Orchestrator
└── agents/                            # Role definitions
    ├── implementer.md
    ├── reviewer.md
    └── fixer.md
```

## Adding a Skill

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

Then run `deploy-skills claude` from your project.

## BA Skills

Most BA skills (problem-thesis, stakeholder, requirements, etc.) live in the [superpowers plugin](https://github.com/anthropics/superpowers) rather than this repo. The `ba-adversarial-review` skill here is the exception — it's a standalone Claude Code skill for adversarial review of BA deliverables.

## Platform Notes

- Claude Code loads `SKILL.md` files from `.claude/skills/` automatically
- Skills can reference sub-files using relative paths
- Project-specific skills go in `.claude/skills/_project/` (never overwritten by deploy)
- Personal overrides go in `CLAUDE.local.md` (add `@CLAUDE.local.md` to your project's CLAUDE.md)
- Some projects may also carry local skills such as `ship`, `deploy`, or debugging helpers; keep those in `_project/` rather than the shared published set
