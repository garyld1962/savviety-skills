---
description: >-
  List all available custom prompts by category with descriptions, or show
  detailed help for a specific prompt. Covers the full prompt library across
  ba/, dev/, review/, and common/ — and clarifies when to use a custom prompt
  vs. a Copilot built-in (/plan, /review, /research, /fleet, /tasks, /diff,
  /pr, /skills). Run with no argument to get the full catalogue; pass a prompt
  name to see usage, arguments, and when to reach for it.
argument-hint: '[prompt-name]'
---

# Prompt Reference — Copilot Edition

List the available custom prompt library or get deep help on a specific prompt.

## Copilot Built-ins vs. Custom Prompts

Copilot ships built-in slash commands. Prefer them for their native purposes:

| Built-in | Best for |
|----------|----------|
| `/plan` | Generating an implementation plan from a task description |
| `/review` | Quick broad code review of changed files |
| `/research` | Answering questions about a codebase or technology |
| `/fleet` | Multi-file edits across a workspace |
| `/tasks` | Breaking down work into tracked subtasks |
| `/diff` | Summarising and explaining a diff |
| `/pr` | Inspecting an open PR's state, checks, and comments |
| `/skills` | Inspecting installed skills and skill metadata |

Use a custom prompt when you need **governed, reproducible workflows** that go beyond what a built-in provides — e.g. adversarial review lenses, BA specification pipelines, dependency audits, or postmortem generation.

To discover all installed custom prompts (including any added after this prompt was last updated), run `/skills` in the chat input. To find prompts from the community, browse [github.com/github/awesome-copilot](https://github.com/github/awesome-copilot).

---

## List Mode (no argument)

1. Discover all `.github/prompts/**/*.prompt.md` files in the workspace.
2. Read the `description` field from each file's YAML frontmatter.
3. Group by directory using the categories below as defaults. Any prompt not covered goes into **Other**.
4. Present one table per category with prompt name and description.
5. Footer: `Use #prompt:skill-help <name> for details on any prompt.`

### Default Category Map

**BA / Requirements** (`ba/`)

| Prompt | Description |
|--------|-------------|
| `ba-context-builder` | Build a reusable BA project context document capturing stakeholders, terminology, and constraints |
| `ba-eval-harness` | Design a repeatable evaluation suite for scoring AI-generated BA deliverables |
| `ba-knowledge-capture` | Capture BA decisions, stakeholder intelligence, and lessons learned |
| `ba-problem-refiner` | Refine a vague business problem into a precise, solution-neutral problem statement |
| `ba-spec-engineer` | Build an execution-ready BA specification through structured interview and testable acceptance criteria |
| `ideate` | Explore and shape an idea from a rough ask or document set for mixed business and technical audiences |
| `prd-validate` | Turn a rough story, BRD, or draft into an implementation-ready artifact |
| `ubiquitous-language` | Extract a DDD-style ubiquitous language glossary from conversation and codebase |

**Development** (`dev/`)

| Prompt | Description |
|--------|-------------|
| `audit-existing` | Audit a repo before planning — produces implemented/missing/duplicated/broken checklist without edits |
| `changelog` | Generate a changelog from Conventional Commits, calculate next semver, update CHANGELOG.md |
| `checkpoint` | Run repo-specific quality gate across changed scope (lint, build, test) |
| `code-investigate` | Search one or multiple repos for a code pattern or behavior and produce a Markdown investigation index |
| `dep-audit` | Audit dependency health: security, outdated packages, unused deps, and licenses |
| `dep-migrate` | Produce a repo-specific migration guide for a major dependency or runtime upgrade |
| `execute-plan` | Execute an accepted implementation plan in dependency order |
| `execute-prd` | Read a PRD/RFC, audit repo state, create a validated execution plan, then execute it |
| `execute-workflow` | Governed execution workflow from a requirements artifact with mandatory plan/review/adversarial gates |
| `grill-me` | Stress-test a plan or design by relentlessly interviewing one decision at a time |
| `hotfix` | Apply a minimal, fast-tracked production fix with targeted verification |
| `k8s-verify` | Verify a Kubernetes deployment: namespace, rollouts, pod health, endpoints, events |
| `kickoff` | Start autonomous development from a PRD, story, or repo ask following the repo's full governed flow |
| `modernize` | Audit an older codebase and produce a within-stack refactor plan for `execute-prd --type=refactor` |
| `postmortem` | Run a governed postmortem over a completed execution run and write a structured postmortem.md |
| `pr` | Governed PR lifecycle — branch, commit, checkpoint, push, create PR, optionally squash-merge |
| `prd-acceptance` | Validate a finished implementation against PRD acceptance criteria with concrete evidence |
| `repo-status` | Concise snapshot of repo state — branch, working tree, unpushed commits, stashes, open PRs |
| `ship` | Ship completed work through the repo's actual delivery flow: checkpoint, commit, push, PR, CI |
| `skill-audit` | Audit a Copilot asset set against platform capabilities, or run `--native-overlap` for source-repo prompt overlap with built-ins |
| `skill-help` | This prompt — list or detail custom prompts in the library |
| `sync-main` | Sync current branch with main via fetch and rebase, with conflict resolution guidance |
| `test-plan` | Create or refresh a TDD-first test plan matching the repo's real test framework |
| `triage` | Investigate a bug from reproduction through root cause analysis; produces a structured triage report |
| `what-is-it-about` | YouTube video thesis and outline tool |
| `work-item` | Retrieve and normalise a work item from Azure DevOps or Linear for planning and BA workflows |

**Review** (`review/`)

| Prompt | Description |
|--------|-------------|
| `domain-review` | Structured defect-focused review for correctness, tests, async, API contract, and data integrity |
| `code-review-professional` | Senior-bar engineering review for design and implementation quality at realistic scale |
| `review-adversarial` | Cross-model code review via skeptic, architect, and minimalist lenses — produces a persisted report |
| `review-api` | Targeted API and service review: validation, auth, async, and contract focus |
| `review-db` | Targeted database review: schema, migration safety, query, and data-integrity focus |
| `review-design` | Targeted UI review against the project's design system and accessibility conventions |
| `review-gauntlet` | Cross-model adversarial review challenge — run with a different model selected in the model picker |
| `review-tests` | Targeted test review: coverage, behaviour, async, and isolation using project test conventions |
| `spec-review-adversarial` | Adversarial review of PRDs, requirements, and acceptance criteria; returns PASS/CONTESTED/REJECT |

**Common** (`common/`)

| Prompt | Description |
|--------|-------------|
| `configure` | Fill in blank config templates for other prompts by interviewing the user |
| `env-check` | Detect shell and OS, determine safe command routing for multi-environment repos |

---

## Detail Mode (`<name>` provided)

1. Find the matching `.github/prompts/**/<name>.prompt.md` file.
2. Read the full file and present:
   - **Description** from frontmatter
   - **Arguments** — the `argument-hint` and any argument documentation in the body
   - **When to use** — including when to prefer a Copilot built-in instead
   - **Workflow summary** — major phases or steps (headings only, not full content)
3. Keep it concise — enough to use the prompt without reading the source.

---

## Rules

- Discover from filesystem — don't hardcode the catalogue as gospel; any prompt not in the table goes to **Other**.
- User-invokable prompts only — never list agents/ or internal-only files.
- Use "prompt" terminology (not "skill") — this is the Copilot context.
- Always surface the built-in alternative when one exists.
