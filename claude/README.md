# Claude Code Skills

Skills for **Claude Code** (Anthropic's CLI). Invoked as `/name` in conversations.

## Setup

This directory is the **source-authoring tree** for shared Claude assets. In a
real project, the deployed runtime layout is different:

| Source in this repo | Project destination | Notes |
|---|---|---|
| `claude/<skill>/` | `.claude/skills/<skill>/` | Shared user-invokable skills |
| `claude/_internal/` | `.claude/skills/_internal/` | Internal callable contracts and rubrics; hidden from normal help |
| `claude/infra/<asset>/` | `.claude/<asset>/` | Hook and utility scripts; not installed as skills |
| `claude/settings.template.json` | `.claude/settings.json` | Optional starter for permissions and hooks |
| `templates/CLAUDE.local.md` | `CLAUDE.local.md` | Personal local overrides; never overwrite once created |
| `claude/README.md`, `claude/MODEL-POLICY.md`, `claude/SESSION-CONTEXT.md` | Do not copy into `.claude/skills/` | Source docs and reference material |

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
| kickoff | `/kickoff` | Interactive readiness → plan → implement → review |
| execute-prd | `/execute-prd` | Convert PRD/work-item context into a plan and execute it |
| execute-plan | `/execute-plan` | Execute a plan file with task-by-task validation |
| validate-plan | `/validate-plan` | Validate that a written plan is ready to execute |
| checkpoint | `/checkpoint` | Quality gate: lint, build, tests for changed scope |
| ship | `/ship` | Move completed work through the repo's delivery flow |
| pr | `/pr` | Create and merge a pull request from the current branch |
| hotfix | `/hotfix` | Fast-path emergency fix workflow |
| changelog | `/changelog` | Generate or update changelog content from repo changes |
| sync-main | `/sync-main` | Sync the current branch with main safely |
| audit-existing | `/audit-existing` | Audit an existing implementation against test and delivery expectations |
| parallel-optimization | `/parallel-optimization` | Restructure a plan for safe parallel execution |
| process-tune | `/process-tune` | Tune shared workflow rules from repeated run evidence |
| issue-slices | `/issue-slices` | Break a PRD into independently-grabbable GitHub issues as vertical slices |
| modernize | `/modernize` | Audit a codebase against current AI toolchain capability and produce a refactor plan |

### Requirements, Design & BA

| Skill | Invocation | Purpose |
|-------|------------|---------|
| prd-validate | `/prd-validate` | Turn a PRD, story, or rough spec into an implementation-ready AERS (rubric: `_internal/aers-readiness/`) |
| prd-acceptance | `/prd-acceptance` | Validate whether delivered work satisfies the PRD/acceptance bar |
| spec-review-adversarial | `/spec-review-adversarial` | Adversarial review of specs, requirements, stories, and acceptance criteria |
| ideate | `/ideate` | Explore solution directions before detailed planning |
| thesis | `/thesis` | Interrogate for a single-sentence product or architectural thesis, then audit scope against it |
| grill-me | `/grill-me` | Stress-test a plan or design by walking decision branches |
| ubiquitous-language | `/ubiquitous-language` | Build a shared business/domain vocabulary |
| what-is-it-about | `/what-is-it-about` | Extract a thesis and outline from a YouTube/video artifact |
| goal | `/goal` | Clarify and validate a development goal before writing a PRD |
| design-twice | `/design-twice` | Explore multiple radically different designs before committing |
| refactor-brief | `/refactor-brief` | Plan a refactor through interview and file it as a GitHub issue RFC |
| drawio | `/drawio` | Generate native .drawio diagrams (flowcharts, ER, sequence, class, architecture) |

### Review & Investigation

| Skill | Invocation | Purpose |
|-------|------------|---------|
| domain-review | `/domain-review` | Domain-based review controller with profiles and overlays |
| code-review-professional | `/code-review-professional` | Seniority-calibrated craft grading for a code change |
| review-adversarial | `/review-adversarial` | Cross-model adversarial review |
| review-gauntlet | `/review-gauntlet` | Meta-review that challenges review output itself |
| code-investigate | `/code-investigate` | Evidence-backed code investigation across one or more repos |
| triage | `/triage` | Investigate a bug through reproduction and root-cause analysis |
| postmortem | `/postmortem` | Retrospective analysis after delivery or incident work |
| test-plan | `/test-plan` | Build or refresh a TDD-first test plan |
| bug-session | `/bug-session` | Interactive bug-reporting session that files durable GitHub issues |

### Review Skills Decision Matrix

Several review skills overlap with Claude Code built-ins. Use this matrix to pick the right one:

| Situation | Skill | Why |
|---|---|---|
| Standard PR review on a small/medium diff | `/review` (built-in) | Fastest path; no project-specific setup needed |
| Security-focused pass on pending changes | `/security-review` (built-in) | Purpose-built for vulnerability classes |
| Domain-aware review (frontend, DB, API, design tokens) | `/domain-review` | Orchestrates specialist lenses per changed file |
| High-stakes diff (200+ lines, auth/payments/migrations) | `/review-adversarial` | Runs on a **different model** to challenge assumptions |
| Challenging an existing review's conclusions | `/review-gauntlet` | Meta-review — attacks the review itself, not the code |
| Specs / requirements / acceptance criteria — not code | `/spec-review-adversarial` | Targets ambiguity in specs before they become defects |
| Test suite coverage & quality audit | `review-tests` (external skill, not shipped from this repo) | Behavior-focused test review |
| Workflow retrospective after a governed run | `/postmortem` | Reviews the process, not the code |

**Compose, don't duplicate:** `/pr` and `/ship` already call `/checkpoint` internally; don't run both. `/review-adversarial` is an *optional* follow-up after `/domain-review` passes, not a replacement.

### Operations, Environment & Configuration

| Skill | Invocation | Purpose |
|-------|------------|---------|
| configure | `/configure` | Fill project or user config templates used by shared skills |
| env-check | `/env-check` | Detect shell/environment routing before giving commands |
| k8s-verify | `/k8s-verify` | Post-deploy Kubernetes verification |
| dep-audit | `/dep-audit` | Audit dependency health and risk |
| dep-migrate | `/dep-migrate` | Plan major-version dependency migrations |
| work-item | `/work-item` | Fetch Azure DevOps or Linear work-item context |
| repo-status | `/repo-status` | Show live branch, worktree, push, stash, and PR state |
| gh-readiness | `/gh-readiness` | Verify GitHub CLI is installed, authenticated, and reachable before PR/issue/release skills run |

### Session & Meta

| Skill | Invocation | Purpose |
|-------|------------|---------|
| skill-help | `/skill-help` | Discover available shared and local Claude skills |
| skill-audit | `/skill-audit` | Audit skill and plugin ecosystem coverage |
| feature-sweep | `/feature-sweep` | Audit installed skills against new Claude Code/API releases and propose integrations |
| vault | `/vault` | Search, create, and manage notes in the Obsidian vault |

### Utilities (not slash commands)

Non-skill assets that ship alongside the skills — typically hooks or shared scripts. These do NOT have `SKILL.md` files and are not invokable via `/name`.

| Asset | Purpose |
|-------|---------|
| pr-guardrail | PreToolUse hook that intercepts `gh pr create` and warns about existing open PRs. See `claude/infra/pr-guardrail/INSTALL.md` |
| journal | Session journal hook scripts. Installed to `.claude/journal/`. |
| install-scan | Dependency/install scanning hook scripts. Installed to `.claude/install-scan/`. |

## Starting execution from a PRD or AERS

Once you have a `PRD.md`, `AERS.md`, or similar requirements artifact, execution
does **not** start automatically. You trigger it by invoking one of the Claude
workflow skills against that file.

### Standard path

| Use case | Trigger |
|---|---|
| Lightweight autonomous implementation | `/kickoff PRD.md` |
| PRD-to-execution path | `/execute-prd PRD.md` |
| Manual staged path | `/prd-validate PRD.md` → write a plan → `/validate-plan ...` → `/execute-plan <plan-file>` |

### Typical flow

1. **Read the artifact** (`PRD.md`, `AERS.md`, story, or spec).
2. **Run readiness** if ambiguity remains (`/prd-validate` directly, or via
   `/kickoff` / `/execute-prd`).
3. **Plan** once the artifact is ready enough to build.
4. **Execute** with `/execute-plan` or let `/kickoff` / `/execute-prd`
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
domain-review/
├── SKILL.md                           # Orchestrator
├── concept/                            # Base review lenses
├── dialect/                            # Language-specific overlays
├── platform/                           # Platform/infrastructure overlays
├── profiles/                           # Review profile YAML
└── references/                         # Controller support docs

test-plan/
├── SKILL.md                           # Orchestrator
├── foundations/                        # Shared schemas, rubrics
├── analysts/                          # Domain-specific analysts
└── test-writer/SKILL.md               # Test case writer

execute-plan/
├── SKILL.md                           # Orchestrator
├── workflows/
│   └── run-plan.mjs                   # Workflow tool script
└── tests/                             # Harness smoke tests

_internal/
├── aers-readiness/SKILL.md             # Internal callable rubric
├── decision-record/SKILL.md            # Internal callable contract
├── dependency-classification/SKILL.md  # Internal callable contract
├── diff-manifest/SKILL.md              # Internal callable contract
├── disposition/SKILL.md                # Internal callable contract
├── modernization-rubric/SKILL.md       # Internal callable rubric
├── plan-format/SKILL.md                # Internal callable contract
├── pre-flight-check/SKILL.md           # Internal callable contract
├── professional-rubric/SKILL.md        # Internal callable rubric
├── repo-delivery/SKILL.md              # Internal callable contract
├── security-quick-check/SKILL.md       # Internal callable contract
└── closed-decisions/                   # Fragment store (not a skill)
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

Most BA discipline skills (problem-thesis, stakeholder, requirements, etc.) live in the [superpowers plugin](https://github.com/anthropics/superpowers) rather than this repo. The local `ubiquitous-language` skill provides a DDD glossary workflow. Adversarial review of specs, validation of PRDs against the AERS rubric, and acceptance verification of delivered work live as user-invokable skills (`/spec-review-adversarial`, `/prd-validate`, `/prd-acceptance`) since they're spec-engineering / verification concerns rather than core BA elicitation.

## Platform Notes

- Claude Code loads `SKILL.md` files from `.claude/skills/` automatically
- Project permissions and hooks usually live in `.claude/settings.json`; start
  from `claude/settings.template.json` if you need a neutral baseline
- Skills can reference sub-files using relative paths
- Claude worker roles may be nested under a skill (for example
  `teams/agents/*.md`) or represented as private resources such as
  analysts and writers under the owning skill
- Internal callable contracts live under `_internal/` and should not be listed
  in normal user help
- Review/fix loops should dispatch a **fresh** worker for each pass rather than
  assuming an earlier worker conversation can be resumed
- Project-specific skills go in `.claude/skills/_project/` (never overwritten by
  shared-skill sync)
- Personal overrides go in `CLAUDE.local.md` (add `@CLAUDE.local.md` to your project's CLAUDE.md)
- Some projects may also carry local skills such as `ship`, `deploy`, or debugging helpers; keep those in `_project/` rather than the shared published set
