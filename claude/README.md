# Claude Code Skills

Skills for **Claude Code** (Anthropic's CLI). Invoked as `/name` in conversations.

## Setup

This directory is the **source-authoring tree** for shared Claude assets. In a
real project, the deployed runtime layout is different:

| Source in this repo | Project destination | Notes |
|---|---|---|
| `claude/<skill>/` | `.claude/skills/<skill>/` | Shared user-invokable skills |
| `claude/_rubrics/` | `.claude/skills/_rubrics/` | Shared reference material |
| `claude/settings.template.json` | `.claude/settings.json` | Optional starter for permissions and hooks |
| `templates/CLAUDE.local.md` | `CLAUDE.local.md` | Personal local overrides; never overwrite once created |
| `claude/README.md`, `claude/SESSION-CONTEXT.md` | Do not copy into `.claude/skills/` | Source docs and reference material |

If you're testing directly from this source repo, copy the shared skill folders
into `.claude/skills/` with that mapping. If you're consuming a published
bundle, use its install/sync workflow instead of copying from this tree by
hand.

## Skill Catalog

This README lists the **shared Claude skills in this repo**. Claude projects may
also have additional skills from plugins such as `superpowers` or from
project-local `.claude/skills/_project/` content.

### Execution & Delivery

| Skill | Invocation | Purpose |
|-------|------------|---------|
| kickoff | `/kickoff` | Start autonomous development from a PRD, story, or AERS |
| plan | `/plan` | Create an implementation plan from requirements |
| execute-plan | `/execute-plan` | Execute a plan file with task-by-task validation |
| execute-workflow | `/execute-workflow` | Run the governed execution workflow with review artifacts |
| checkpoint | `/checkpoint` | Quality gate: lint, build, tests for changed scope |
| ship | `/ship` | Move completed work through the repo's delivery flow |
| pr | `/pr` | Create and merge a pull request from the current branch |
| hotfix | `/hotfix` | Fast-path emergency fix workflow |
| teams | `/teams` | Run 2-4 parallel implementation streams with nested worker roles |
| changelog | `/changelog` | Generate or update changelog content from repo changes |
| sync-main | `/sync-main` | Sync the current branch with main safely |

### Requirements, Design & BA

| Skill | Invocation | Purpose |
|-------|------------|---------|
| prd-readiness | `/prd-readiness` | Evaluate whether a requirements artifact is execution-ready |
| prd-validate | `/prd-validate` | Turn a PRD, story, or rough spec into an implementation-ready AERS |
| prd-acceptance | `/prd-acceptance` | Validate whether delivered work satisfies the PRD/acceptance bar |
| ideate | `/ideate` | Explore solution directions before detailed planning |
| grill-me | `/grill-me` | Stress-test a plan or design by walking decision branches |
| ubiquitous-language | `/ubiquitous-language` | Build a shared business/domain vocabulary |
| ba-review-adversarial | `/ba-review-adversarial` | Adversarial review of BA deliverables |

### Review & Investigation

| Skill | Invocation | Purpose |
|-------|------------|---------|
| code-review | `/code-review` | Domain-based review controller with profiles and overlays |
| review-adversarial | `/review-adversarial` | Cross-model adversarial review |
| review-gauntlet | `/review-gauntlet` | Meta-review that challenges review output itself |
| code-investigate | `/code-investigate` | Evidence-backed code investigation across one or more repos |
| triage | `/triage` | Investigate a bug through reproduction and root-cause analysis |
| postmortem | `/postmortem` | Retrospective analysis after delivery or incident work |
| test-plan | `/test-plan` | Build or refresh a TDD-first test plan |

### Review Skills Decision Matrix

Several review skills overlap with Claude Code built-ins. Use this matrix to pick the right one:

| Situation | Skill | Why |
|---|---|---|
| Standard PR review on a small/medium diff | `/review` (built-in) | Fastest path; no project-specific setup needed |
| Security-focused pass on pending changes | `/security-review` (built-in) | Purpose-built for vulnerability classes |
| Domain-aware review (frontend, DB, API, design tokens) | `/code-review` | Orchestrates specialist lenses per changed file |
| High-stakes diff (200+ lines, auth/payments/migrations) | `/review-adversarial` | Runs on a **different model** to challenge assumptions |
| Challenging an existing review's conclusions | `/review-gauntlet` | Meta-review — attacks the review itself, not the code |
| BA deliverables (requirements, stories, AC) — not code | `/ba-review-adversarial` | Targets ambiguity in specs before they become defects |
| Test suite coverage & quality audit | `review-tests` (superpowers) | Behavior-focused test review |
| Workflow retrospective after a governed run | `/postmortem` | Reviews the process, not the code |

**Compose, don't duplicate:** `/pr` and `/ship` already call `/checkpoint` internally; don't run both. `/review-adversarial` is an *optional* follow-up after `/code-review` passes, not a replacement.

### Operations, Environment & Configuration

| Skill | Invocation | Purpose |
|-------|------------|---------|
| configure | `/configure` | Fill project or user config templates used by shared skills |
| env-check | `/env-check` | Detect shell/environment routing before giving commands |
| k8s-verify | `/k8s-verify` | Post-deploy Kubernetes verification |
| dep-audit | `/dep-audit` | Audit dependency health and risk |
| dep-migrate | `/dep-migrate` | Plan major-version dependency migrations |
| work-item | `/work-item` | Fetch Azure DevOps or Linear work-item context |

### Session & Meta

| Skill | Invocation | Purpose |
|-------|------------|---------|
| whereami | `/whereami` | Restore session/project context |
| session-save | `/session-save` | Persist session context for later restoration |
| skill-help | `/skill-help` | Discover available shared and local Claude skills |
| skill-audit | `/skill-audit` | Audit skill and plugin ecosystem coverage |
| find-skills | `/find-skills` | Discover installable ecosystem skills for a given need |

## Starting execution from a PRD or AERS

Once you have a `PRD.md`, `AERS.md`, or similar requirements artifact, execution
does **not** start automatically. You trigger it by invoking one of the Claude
workflow skills against that file.

### Standard path

| Use case | Trigger |
|---|---|
| Lightweight autonomous implementation | `/kickoff PRD.md` |
| Governed execution with review/disposition artifacts | `/execute-workflow PRD.md` |
| Manual staged path | `/prd-validate PRD.md` → `/plan ...` → `/execute-plan <plan-file>` |

### Typical flow

1. **Read the artifact** (`PRD.md`, `AERS.md`, story, or spec).
2. **Run readiness** if ambiguity remains (`/prd-validate` directly, or via
   `/kickoff` / `/execute-workflow`).
3. **Plan** with `/plan` once the artifact is ready enough to build.
4. **Execute** with `/execute-plan` or let `/kickoff` / `/execute-workflow`
   carry the workflow through implementation and review.

## Multi-File Skills

Claude does **not** use a separate top-level agent asset layer in this repo the
way Copilot Native does. Instead, worker roles usually appear in one of two
forms:

1. **Nested worker-role files inside a skill** when the role is private to that
   workflow.
2. **Subskills / specialist skill directories** when the role is reusable and
   worth composing elsewhere.

Some shared Claude workflows therefore have sub-files for specialists,
analysts, worker prompts, or foundations:

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

The important architectural distinction is **private worker role vs reusable
capability**, not "does Claude have a top-level `agents/` folder?".

Claude subagents are also **fresh conversations per dispatch**. Do not assume a
worker can be resumed later via `SendMessage`. For review-and-fix loops,
dispatch a fresh fix worker with the findings, scope, and files it should touch.

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

Then sync it into target projects using your current published/shared-skills
workflow, or copy `claude/my-skill/` into `.claude/skills/my-skill/` when
testing manually from the source repo.

## BA Skills

Most BA skills (problem-thesis, stakeholder, requirements, etc.) live in the [superpowers plugin](https://github.com/anthropics/superpowers) rather than this repo. The `ba-adversarial-review` skill here is the exception — it's a standalone Claude Code skill for adversarial review of BA deliverables.

## Platform Notes

- Claude Code loads `SKILL.md` files from `.claude/skills/` automatically
- Project permissions and hooks usually live in `.claude/settings.json`; start
  from `claude/settings.template.json` if you need a neutral baseline
- Skills can reference sub-files using relative paths
- Claude worker roles may be nested under a skill (for example
  `teams/agents/*.md`) or represented as subskills such as specialists,
  analysts, and writers
- Review/fix loops should dispatch a **fresh** worker for each pass rather than
  assuming an earlier worker conversation can be resumed
- Project-specific skills go in `.claude/skills/_project/` (never overwritten by
  shared-skill sync)
- Personal overrides go in `CLAUDE.local.md` (add `@CLAUDE.local.md` to your project's CLAUDE.md)
- Some projects may also carry local skills such as `ship`, `deploy`, or debugging helpers; keep those in `_project/` rather than the shared published set
