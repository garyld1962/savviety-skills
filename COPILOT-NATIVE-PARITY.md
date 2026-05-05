# Claude Canonical ↔ Copilot-Native Parity Plan

**Purpose:** Identify which enhancements from `copilot-native/` should be incorporated into the Claude Code canonical format under `claude/`, where Claude Code built-ins already provide equivalent or better functionality, and what should be left behind.

**Scope:** Two canonical systems going forward — `claude/` and `copilot-native/`. The `vscode/` tree is **deprecated** and will be retired. `MAPPING.md` (which tracks claude↔vscode parity) becomes historical once this port completes.

**Audience:** Gary, for review before scheduling implementation work.

## Architecture Principles

**Decided in this round:**

1. **Two canonical systems only.** `claude/` for Claude Code, `copilot-native/` for GitHub Copilot (VS Code integration + Copilot CLI). `vscode/` is deprecated.

2. **Environment-neutral canon.** Canonical skills never hardcode environmental specifics: shells (PowerShell/WSL/bash), hostnames, project names, tool choices (npm/yarn/pnpm), specific paths, or specific build commands. Skills describe *abstract patterns*. Variable data lives in **user-editable config/template files** that the skill references. Every skill that depends on environmental data must explicitly tell the user which file to edit.

3. **Template file conventions:**
   - **Per-user global:** `~/.claude/env.config.md` (shell routing, host conventions)
   - **Per-project:** the project's `CLAUDE.md` (build/test commands, delivery flow, ship targets)
   - **Per-skill defaults:** `claude/<skill>/config.template.md` (shipped as a blank template; user copies to `~/.claude/<skill>.config.md` or project `.claude/<skill>.config.md` and edits)
   - **Process docs (governance cluster only):** `docs/runs/`, `docs/process/*.md`, `docs/templates/*.template.md` inside the *consuming* project — not inside the canonical skill

4. **Existing `claude/` skills are already env-neutral** (verified). This port must not break that. New ports from copilot-native must strip environmental bake-in that exists in the source.

---

## 1. Canonical Format Reference

Both systems share a 4-asset taxonomy but use different file shapes and different runtime primitives.

| Asset | Claude canonical (this repo) | Claude Code runtime | Copilot-native (this repo) | Copilot CLI runtime |
|---|---|---|---|---|
| User-invokable workflow | `claude/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` (Skill tool) | `copilot-native/prompts/**/*.prompt.md` | `.github/prompts/**` |
| Durable knowledge / rubric | Sub-files inside a skill dir | Loaded via skill `@reference` | `copilot-native/skills/<name>/SKILL.md` | `.github/skills/<name>/SKILL.md` |
| Bounded specialist worker | Agent tool with `subagent_type` | Built-in + plugin subagents | `copilot-native/agents/<name>.agent.md` | `.github/agents/<name>.agent.md` |
| Always-on passive rule | `CLAUDE.md` (project) or global | `CLAUDE.md` | `copilot-native/instructions/*.instructions.md` | `.github/instructions/*.instructions.md` |
| Repo-wide source of truth | `CLAUDE.md` | `CLAUDE.md` | `copilot-instructions.md` | `.github/copilot-instructions.md` |

**Key architectural difference:** Copilot treats skills, prompts, agents, and instructions as four peer file types. Claude Code treats "skill" as the umbrella and uses the Agent tool for subagents. Plugins bundle groups of skills + subagents.

---

## 2. Current State

### Claude canonical (`claude/`) — 31 skills

| Category | Skills |
|---|---|
| Dev workflow | plan, execute-plan, hotfix, triage, changelog, checkpoint, code-review, pr, teams, test-plan, sync-main, k8s-deploy-verify, dependency-audit, migration-guide, acceptance, work-item |
| Review | adversarial-review, review-gauntlet, review-api, review-db, review-design, review-tests |
| BA | ba-adversarial-review |
| Technology | typescript-advanced-types, next-best-practices, vercel-composition-patterns, vercel-react-best-practices, agent-browser |
| Utility | find-skills, skill-audit |

### Copilot-native — 28 prompts, 12 agents, 22 skills, 3 instructions

**Design philosophy** (from `platform-review.md` and `copilot-native/README.md`): "built-in first." Custom prompts exist only to fill gaps that platform built-ins (`/plan`, `/review`, `/research`, `/tasks`, `/delegate`, `/agent`) cannot handle cleanly.

---

## 3. Claude Code Built-in Coverage

Before recommending ports, here is the built-in functionality already available in Claude Code (via official plugins, subagents, and core features):

### Core platform
- **Agent tool** with `subagent_type` — maps to Copilot agents
- **Task tracking** (TaskCreate / TaskUpdate)
- **Slash commands** via skill invocation
- **CLAUDE.md** for always-on rules — maps to instructions

### Superpowers plugin (installed)
- `brainstorming` — creative exploration before implementation
- `writing-plans` / `executing-plans` — full planning + execution pipeline with checkpoints
- `test-driven-development` — TDD discipline
- `systematic-debugging` — structured debugging
- `verification-before-completion` — evidence-based completion
- `subagent-driven-development` — parallel task execution
- `dispatching-parallel-agents` — 2+ independent tasks in parallel
- `requesting-code-review` / `receiving-code-review` — review loop
- `finishing-a-development-branch` — merge/PR/cleanup
- `using-git-worktrees` — isolated branch workspaces

### Other installed plugins
- `ba-*` (13 skills) — full BA pipeline: init, context-builder, problem-thesis, problem-refiner, current-state, requirements, validation, solution, stakeholder, preflight, eval-harness, knowledge-capture, spec-engineer
- `feature-dev:feature-dev` + `code-architect` / `code-reviewer` / `code-explorer` subagents
- `commit-commands:commit` / `commit-push-pr` / `clean_gone`
- `pr-review-toolkit:review-pr` + type-design-analyzer / code-reviewer / silent-failure-hunter / comment-analyzer / pr-test-analyzer / code-simplifier subagents
- `claude-md-management:revise-claude-md` / `claude-md-improver`
- `checkpoint:checkpoint`
- `simplify:simplify`
- `differential-review:diff-review`
- `static-analysis:semgrep` / `codeql` / `sarif-parsing`
- `variant-analysis:variants`

---

## 4. Gap Analysis (Copilot-native → Claude canonical)

Status legend: `MISSING` (no equivalent in claude/ or built-ins) · `BUILT-IN` (covered by Claude Code built-ins, no port needed) · `=` (already ported) · `ENHANCE` (exists but copilot-native version adds value)

### 4a. Prompts (28 items)

| Copilot-native prompt | Claude equivalent | Status | Notes |
|---|---|---|---|
| **ba/ideate** | — | MISSING | Mixed business + tech ideation (single prompt wraps both lenses). No 1:1 Claude plugin equivalent. |
| **ba/prd-validator** | `claude/prd-acceptance` (partial) | MISSING | *Pre*-implementation AERS readiness gate. Acceptance is *post*-implementation. Different stages. |
| **ba/ba-problem-refiner** | `ba-problem-refiner` plugin | BUILT-IN | Use plugin. |
| **ba/ba-spec-engineer** | `ba-spec-engineer` plugin | BUILT-IN | Use plugin. |
| **ba/ba-context-builder** | `ba-context-builder` plugin | BUILT-IN | Use plugin. |
| **ba/ba-eval-harness** | `ba-eval-harness` plugin | BUILT-IN | Use plugin. |
| **ba/ba-knowledge-capture** | `ba-knowledge-capture` plugin | BUILT-IN | Use plugin. |
| **common/environment-check** | — | MISSING | PowerShell/WSL/Linux shell routing. Claude Code has no built-in for this. Small but valuable for your Windows laptop + WSL workflow. |
| **dev/ado-item** | `claude/work-item` | = | Already ported. |
| **dev/adversarial-review** | `claude/review-adversarial` | = | Already ported. Evaluate enhancement (model-switch discipline). |
| **dev/autonomous-development-kickoff** | `superpowers:writing-plans` + `executing-plans` (partial) | MISSING | Built-in path is thinner. Copilot version adds: (1) readiness gate before planning, (2) small-change fast path, (3) explicit environment detection gate. |
| **dev/checkpoint** | `claude/checkpoint` + `checkpoint:checkpoint` plugin | = | Already covered. |
| **dev/copilot-asset-audit** | — | SKIP | Copilot-platform-specific. Not applicable. |
| **dev/dependency-audit** | `claude/dep-audit` | = | Already ported. |
| **dev/execute-plan** | `claude/execute-plan` + `superpowers:executing-plans` | = | Already covered. |
| **dev/execute-workflow** | — | MISSING | **Governed execution** with required artifacts (review-plan, review-code, adversarial-review, disposition-log). Distinct from execute-plan — adds governance layer. |
| **dev/hotfix** | `claude/hotfix` | = | Already ported. |
| **dev/investigate-code** | — | MISSING | Cross-repo code investigation with structured JSON match schema + versioned Markdown reports. |
| **dev/k8s-deploy-verify** | `claude/k8s-verify` | = | Already ported. |
| **dev/migration-guide** | `claude/dep-migrate` | = | Already ported. |
| **dev/postmortem** | — | MISSING | Structured retrospective tied to governed-run artifacts. No built-in equivalent. |
| **dev/ship** | — | MISSING (as canonical) | Exists only as `_project/ship` in Baker Street. Canonical version would codify delivery flow. |
| **dev/test-plan** | `claude/test-plan` | = | Already ported. Evaluate rubric merge. |
| **review/adversarial-review-gauntlet** | `claude/review-gauntlet` | = | Already in parity per `MAPPING.md`. Same Skeptic/Architect/Pragmatist lenses, same verdict vocabulary. |
| **review/review-api** | `claude/review-api` | = | Already ported. |
| **review/review-db** | `claude/review-db` | = | Already ported. |
| **review/review-design** | `claude/review-design` | = | Already ported. |
| **review/review-tests** | `claude/review-tests` | = | Already ported. |

### 4b. Skills — 22 items (reusable rubrics)

| Copilot-native skill | Claude equivalent | Status | Notes |
|---|---|---|---|
| **review-disposition-governance** | — | MISSING | Core governance artifact: status vocabulary (`open`/`fixed`/`disagree-with-evidence`/`defer`/`accepted-risk`/`resolved`), disposition loop, blocking rule, senior-baseline principle, elevation pass, proof accounting. High value. |
| **review-foundations** | — | MISSING | Shared evidence/verdict rules used by all review-* specialists. Base class for the review cluster. |
| **repo-delivery** | — | MISSING | Delivery playbook referenced by execute-plan, checkpoint, ship, hotfix. |
| **execution-environment** | — | MISSING | Shell-routing rules (pairs with environment-check prompt). |
| **prd-readiness** | — | MISSING | Interactive readiness checklist. Drives prd-validator prompt + prd-quality-gate agent. |
| **copilot-platform-playbook** | — | SKIP | Copilot-platform-specific. |
| **project-context** | `ba-context-builder` plugin | BUILT-IN | Plugin covers this. |
| **ba-knowledge-ops** | `ba-knowledge-capture` + `ba-eval-harness` plugins | BUILT-IN | Plugins cover this. |
| **ba-ideation** | — | MISSING (paired with ideate prompt) | Workshop-ready outputs. |
| **tech-ideation** | `superpowers:brainstorming` (partial) | BUILT-IN? | Brainstorming is more open-ended; tech-ideation is architecture-specific. Evaluate. |
| **adversarial-review** | `claude/review-adversarial` | = | Already ported. |
| **test-planning** | `claude/test-plan` | = | Evaluate rubric merge — copilot-native version may add checklists. |
| **test-quality** | Used internally by `claude/review-tests` | = | Already covered. |
| **api-patterns** | Used internally by `claude/review-api` | = | Already covered. |
| **db-schema-review** | Used internally by `claude/review-db` | = | Already covered. |
| **ui-design-compliance** | Used internally by `claude/review-design` | = | Already covered. |
| **k8s-verification** | Used internally by `claude/k8s-verify` | = | Already covered. |
| **dependency-change-management** | Used internally by `claude/dep-audit` + `claude/dep-migrate` | = | Already covered. |
| **ado-work-items** | Used internally by `claude/work-item` | = | Already covered. |
| **code-investigation-orchestrator** | — | MISSING | Part of investigate-code cluster. |
| **code-investigation-search** | — | MISSING | JSON match schema. Part of investigate-code cluster. |
| **investigation-report-writer** | — | MISSING | Versioned Markdown report format. Part of investigate-code cluster. |

### 4c. Agents — 12 items (specialist subagents)

| Copilot-native agent | Claude subagent equivalent | Status | Notes |
|---|---|---|---|
| **code-reviewer** | `feature-dev:code-reviewer` / `pr-review-toolkit:code-reviewer` | BUILT-IN | Plugin subagents cover this. |
| **adversarial-reviewer** | Agent tool + `claude/review-adversarial` skill | = | Spawn via Agent with skill reference. |
| **plan-reviewer** | Agent tool + plan review skill | MISSING | New subagent for plan readiness/proof obligations. |
| **disposition-coordinator** | — | MISSING | Pairs with review-disposition-governance. Reconciles findings into disposition log. |
| **execute-orchestrator** | — | MISSING | Drives the governed workflow. |
| **postmortem-analyst** | — | MISSING | Pairs with postmortem prompt. |
| **prd-quality-gate** | — | MISSING | Pairs with prd-validator prompt. |
| **orchestrator-code-investigation** | `Explore` subagent (partial) | MISSING | Explore is single-scope; this coordinates multi-repo investigations. |
| **specialist-code-investigation-search** | `Explore` subagent (partial) | MISSING | Different output contract (structured JSON matches). |
| **writer-investigation-report** | — | MISSING | Markdown report formatter. |
| **ba-ideation** | — | MISSING (paired with ideate) | Business ideation facilitator. |
| **tech-ideation** | — | MISSING (paired with ideate) | Technical ideation facilitator. |

### 4d. Instructions — 3 items

| Copilot-native instruction | Claude equivalent | Status | Notes |
|---|---|---|---|
| **execution-environment.instructions.md** | — | MISSING | Always-on shell-routing rules. In Claude Code, belongs in global `CLAUDE.md` (user-level, not project). |
| **copilot-asset-authoring.instructions.md** | — | SKIP | Copilot-platform-specific. |
| **personal.instructions.md** | — | BUILT-IN | Claude Code equivalent is `~/.claude/CLAUDE.md` (already in use). |

---

## 5. Port Plan — New Skills to Add

Organized by cluster, priority-ordered within each. **Each cluster lists the environmental templates you will need to edit** after the port is complete.

### Cluster A: Governed Execution (highest value)

Delivers a distinct workflow beyond `superpowers:executing-plans` — specifically the artifact-based governance, disposition loop, and status vocabulary. This is the largest genuinely-new capability in copilot-native.

| Order | New Claude canonical skill | Source | Dependencies |
|---|---|---|---|
| A1 | `claude/_internal/disposition` | `skills/review-disposition-governance/SKILL.md` | None (foundational, not user-invokable) |
| A2 | `claude/_internal/repo-delivery` | `skills/repo-delivery/SKILL.md` | None (not user-invokable) |
| A3 | `claude/execute-workflow` | `prompts/dev/execute-workflow.prompt.md` | A1, A2 |
| A4 | **`claude/kickoff`** | `prompts/dev/autonomous-development-kickoff.prompt.md` | A1 |
| A5 | `claude/postmortem` | `prompts/dev/postmortem.prompt.md` + `agents/postmortem-analyst.agent.md` | A1 |
| A6 | `claude/ship` | Existing `_project/ship` canonicalized | A2 |
| A7 | `claude/execute-workflow/process-docs.template/` (5 files) | Ship reference process docs as templates | A3 |
| A8 | `claude/execute-workflow/artifact-templates.template/` (6 files) | Ship reference artifact templates | A3 |

**A7 — Reference process docs shipped as templates (per decision on item 1):**

| Template file | Source | User action |
|---|---|---|
| `claude/execute-workflow/process-docs.template/execute-workflow.md` | derived from copilot-native intent | Copy to `<project>/docs/process/`, edit phase ordering for project |
| `claude/execute-workflow/process-docs.template/review-and-disposition.md` | derived from `skills/review-disposition-governance` | Copy, edit review rounds + escalation thresholds |
| `claude/execute-workflow/process-docs.template/evidence-and-artifacts.md` | new — evidence standards | Copy, edit project-specific evidence rules |
| `claude/execute-workflow/process-docs.template/document-schema.md` | new — artifact schemas | Copy, edit schemas if project deviates |
| `claude/execute-workflow/process-docs.template/postmortem-workflow.md` | derived from postmortem prompt | Copy, edit trigger thresholds |

**A8 — Reference artifact templates:**

| Template file | User action |
|---|---|
| `claude/execute-workflow/artifact-templates.template/review-plan.template.md` | Copy to `<project>/docs/templates/`, edit sections if project deviates |
| `claude/execute-workflow/artifact-templates.template/review-code.template.md` | Same |
| `claude/execute-workflow/artifact-templates.template/adversarial-review.template.md` | Same |
| `claude/execute-workflow/artifact-templates.template/disposition-log.template.md` | Same |
| `claude/execute-workflow/artifact-templates.template/execution-report.template.md` | Same |
| `claude/execute-workflow/artifact-templates.template/postmortem.template.md` | Same |

**Environmental templates (YOU will need to edit these per project):**

| Template file | Scope | What you edit |
|---|---|---|
| `<project>/.claude/workflow.config.md` | per-project | Process doc root, template root, run artifact root (e.g., `docs/runs/`). Points the skill at wherever you placed the copied templates. |
| `<project>/docs/process/*.md` | per-project | The 5 copied process docs (A7) — edit content per project. |
| `<project>/docs/templates/*.template.md` | per-project | The 6 copied artifact templates (A8) — edit sections per project. |
| `<project>/CLAUDE.md` ship section | per-project | For `claude/ship`: the actual delivery commands (build/test/tag/release/deploy) for this project. Skill describes phases abstractly; project CLAUDE.md fills in commands. |

**Onramp reduction:** With A7+A8 shipped as copy-and-edit templates, a new project adopts the governed workflow by running something like `cp -r claude/execute-workflow/process-docs.template/ <project>/docs/process/` then editing — rather than authoring 11 files from scratch.

**Note on agents:** In Claude Code, the four governed-workflow agents (execute-orchestrator, plan-reviewer, disposition-coordinator, postmortem-analyst) should be invoked via the Agent tool with task-specific prompts referencing the disposition skill, rather than created as standalone subagents. Only create custom subagents if the orchestration genuinely needs bounded output contracts enforced outside the main loop.

### Cluster B: Code Investigation

Distinct workflow from Explore subagent — produces versioned reports, supports multi-repo scope, enforces a JSON match schema.

| Order | New Claude canonical skill | Source |
|---|---|---|
| B1 | **`claude/code-investigate`** | `prompts/dev/investigate-code.prompt.md` + 3 supporting skills + 3 agents |

Single bundled skill recommended (not 6 separate files). Embed orchestrator/search/report rubrics as sub-files under `claude/code-investigate/`.

**Environmental templates (YOU will need to edit these):**

| Template file | Scope | What you edit |
|---|---|---|
| `~/.claude/code-investigate.config.md` | per-user | Default report output root (e.g., `docs/code-investigations/`), default repo search roots, default confidence threshold. |
| (none needed at project scope) | — | Scope is provided per-invocation as arguments. |

### Cluster C: PRD Readiness

Fills the **pre-implementation** gap. `claude/prd-acceptance` handles post-impl; this handles pre-impl.

| Order | New Claude canonical skill | Source |
|---|---|---|
| C1 | `claude/prd-readiness` | `skills/prd-readiness/SKILL.md` (knowledge — universal rubric) |
| C2 | `claude/prd-validate` | `prompts/ba/prd-validator.prompt.md` + `agents/prd-quality-gate.agent.md` |

**Naming (per Q3 resolution):** `claude/prd-readiness` for the new pre-impl skill; existing `claude/prd-acceptance` stays unchanged for post-impl.

**Environmental templates:** None. PRD readiness rubric is universal. PRD file location detection uses the same pattern as existing `claude/prd-acceptance` (scans common paths).

### Cluster D: Environment Detection

This is the cluster where env-neutrality matters most. The copilot-native source hardcodes PowerShell/WSL/Linux — we must strip that and externalize.

| Order | New Claude canonical skill | Source | Notes |
|---|---|---|---|
| D1 | **`claude/env-check`** | `prompts/common/environment-check.prompt.md` + `skills/execution-environment/SKILL.md` | Skill describes *detection protocol*, reads user config for shell map. |

**Environmental templates (YOU will need to edit these):**

| Template file | Scope | What you edit |
|---|---|---|
| `~/.claude/env.config.md` | per-user global | Your actual shell setup: which hosts use which shells, how to route commands between WSL/pwsh/zsh/bash, any terminal-switching rules. The skill ships a **blank template** with placeholders and section headers; you fill in your homelab specifics (or leave minimal if you only work in one shell). |
| `~/.claude/CLAUDE.md` | per-user global | Short pointer rule: "Before emitting shell commands, check `~/.claude/env.config.md` and route accordingly." 5 lines max. |

**No per-project template needed** — shell routing is a you-problem across all projects.

**Important for Q5 resolution:** The global `~/.claude/CLAUDE.md` gets the short *pointer rule*, not the actual shell list. The shell list lives in the separate editable `env.config.md`. This keeps CLAUDE.md lean and the routing rules editable without touching CLAUDE.md.

### Cluster E: Ideation

Gap between `superpowers:brainstorming` (open-ended) and structured BA/tech ideation.

| Order | New Claude canonical skill | Source |
|---|---|---|
| E1 | `claude/ideate` | `prompts/ba/ideate.prompt.md` + both ideation skills/agents |

**Environmental templates:** None. Ideation workflow is universal.

**Evaluate during port:** If first 30 min of porting reveals `superpowers:brainstorming` + a follow-up BA plugin call covers it, flag and drop.

### Cluster F: Review Foundations (deferred)

Could be a refactor of existing review-* skills to share a base. Lower priority — defer until after Clusters A-E ship.

| Order | Work | Notes |
|---|---|---|
| F1 | Extract `claude/_review-base/` shared rubric | Refactor of existing review-api/db/design/tests |

### Cluster H: Configure skill + pre-flight check pattern (enables every other cluster)

**Problem this solves:** Env-neutral canonical skills ship with blank config templates. Users currently need to read README docs, locate the right template file, copy it, and hand-edit 11+ files to adopt a governed workflow. That onramp is too steep — in practice skills that require config either get skipped or used mis-configured.

**Two-part solution:**

**H1 — New skill: `/configure <target>`** (both platforms)

Interviews the user and fills in blank templates. Invokable standalone or delegated-to from pre-flight checks in other skills.

| Asset | Path |
|---|---|
| Claude | `claude/configure/SKILL.md` |
| Copilot-native | `copilot-native/prompts/common/configure.prompt.md` |

**Behavior:**
- Argument: target name (e.g., `env`, `workflow`, `code-investigate`, `ship`, `copilot-env`)
- Looks up template location from a registry (`claude/configure/registry.md`)
- Reads the blank template, extracts placeholders and required sections
- Asks user one question at a time, pre-populating defaults where possible (detected OS, repo name, git remote, etc.)
- Writes filled result to the destination path
- Supports **re-run** mode: reads existing config, re-prompts only for missing/placeholder fields
- Supports **dry-run** mode: shows what would be written

**Template registry format** (machine-readable, user-editable):
```yaml
env:
  template: claude/env-check/env.config.template.md
  destination: ~/.claude/env.config.md
  required_sections: [shells, hosts, routing_rules]
workflow:
  template: claude/execute-workflow/config.template.md
  destination: "{project}/.claude/workflow.config.md"
  required_fields: [process_docs_root, templates_root, runs_root]
code-investigate:
  template: claude/code-investigate/config.template.md
  destination: ~/.claude/code-investigate.config.md
  required_fields: [report_root, default_repo_roots]
ship:
  template: claude/ship/config.template.md
  destination: "{project}/.claude/ship.config.md"
  required_fields: [build_command, test_command, ship_command]
copilot-env:
  template: copilot-native/templates/env.config.template.md
  destination: $HOME/.copilot/env.config.md
  required_sections: [shells, hosts, routing_rules]
```

**H2 — Pre-flight check pattern** (embedded in every config-dependent skill)

Each high-level skill opens with a **required-info check**. If config is missing or incomplete, halt with an actionable message.

**Pattern (canonical section to add to each affected SKILL.md):**

```markdown
## Pre-flight Required Config

Before proceeding, verify the following:

1. Check `<path>` exists. If not, halt and output:
   "This skill requires <path>.
    Run `/configure <target>` to set it up interactively, or copy the template manually:
    cp ~/repos/skills/claude/<skill>/<template>.md <path>
    then edit."

2. Read the config and verify these fields are present and non-placeholder:
   - field_1
   - field_2

3. If any field is missing or contains placeholder text (`<FILL IN>`, `TODO`, etc.),
   halt with a list of what's missing and the `/configure <target>` invocation.

Only proceed to the main workflow if all required config is present.
```

**Skills that need a pre-flight check (per cluster):**

| Cluster | Skill | Required config | Configure target |
|---|---|---|---|
| A | `claude/execute-workflow` | `<project>/.claude/workflow.config.md` + referenced process docs | `workflow` |
| A | `claude/ship` | `<project>/.claude/ship.config.md` OR `<project>/CLAUDE.md` ship section | `ship` |
| A | `claude/postmortem` | same as execute-workflow (shared config) | `workflow` |
| B | `claude/code-investigate` | `~/.claude/code-investigate.config.md` (SOFT — skill has arg overrides) | `code-investigate` |
| D | `claude/env-check` | `~/.claude/env.config.md` | `env` |
| G | `copilot-native/skills/execution-environment` | `$HOME/.copilot/env.config.md` OR project-level | `copilot-env` |

**Skills that do NOT need pre-flight checks (no required config):**

- `claude/_internal/disposition`, `claude/_internal/repo-delivery` (pure rubrics)
- `claude/kickoff` (references other skills, no direct config)
- `claude/prd-readiness`, `claude/prd-validate` (universal rubrics)
- `claude/ideate` (universal)

**Placeholder convention (used by templates + detected by pre-flight checks):**

- `<FILL IN>` — required, no default possible
- `<FILL IN: example-value>` — required, with hint
- `{{ placeholder_name }}` — programmatic substitution during `/configure`
- `# TODO: ...` — optional guidance comment

**Why Cluster H ships first:** Every other config-dependent skill references it in its pre-flight check. If `/configure` doesn't exist yet, the pre-flight check would still work (fall back to "edit manually" path) but UX degrades to status-quo "read README."

### Cluster G: copilot-native self-heal (env-neutrality)

Now that `copilot-native/` is canonical (not staging), apply the same env-neutral principle to it. Three files contain WSL/PowerShell bake-in with zero macOS/Linux-native routing.

**Current problems in copilot-native:**

| File | Env bake-in |
|---|---|
| `skills/execution-environment/SKILL.md` | Hardcodes PowerShell, WSL, Linux cases. Mentions specific runner names (`.scripts/run.sh`, `.scripts/run.ps1`). Windows-centric — macOS isn't a first-class case. No user-config hook. |
| `instructions/execution-environment.instructions.md` | Same hardcoding at the always-on instruction layer. Auto-applied to `*.sh,ps1,cmd,Makefile` etc. |
| `prompts/common/environment-check.prompt.md` | Thin wrapper around the above — inherits the bake-in. |
| `instructions/personal.instructions.md` | **Already env-neutral** — blank template with commented examples. No change needed. |

**Healing actions:**

| Order | New/modified copilot-native asset | What changes |
|---|---|---|
| G1 | `skills/execution-environment/SKILL.md` — rewrite | Describe abstract **detection protocol** only: detect shell, detect path style, detect runner. Remove all hardcoded case names. Reference user config for routing rules. |
| G2 | `instructions/execution-environment.instructions.md` — rewrite | Thin always-on rule: "Before emitting shell commands, follow the detection protocol in `execution-environment` skill and consult `env.config.md`." Remove all routing cases. |
| G3 | `copilot-native/templates/env.config.template.md` — new | Blank template users copy to `.github/instructions/env.config.md` (or `$HOME/.copilot/env.config.md`) and edit. Structured sections: hosts, shells, runner scripts, terminal-switching rules. |
| G4 | `prompts/common/environment-check.prompt.md` — edit | Strip inherited bake-in. Prompt invokes skill + reads user config. |

**Where the user-config lives (per copilot-native conventions):**

- **Per-user global** → `$HOME/.copilot/env.config.md` (Copilot CLI user-level)
- **Per-project** → `.github/instructions/env.config.md` (already supported via `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`)
- **Local override** → `.github/instructions/personal.instructions.md` (already exists, already preserved from sync)

**Environmental templates (YOU will need to edit these):**

| Template file | Scope | What you edit |
|---|---|---|
| `$HOME/.copilot/env.config.md` | per-user global (Copilot CLI) | Your shell/host routing for all repos. |
| `<project>/.github/instructions/env.config.md` | per-project | Project-specific shell/runner overrides if a project deviates from global. Optional. |

**Rationale:** Gary works across Windows+WSL (Sherlock, Lestrade) AND macOS (Watson, Moriarty, Irene) AND Linux (Mycroft). The current copilot-native execution-environment assets assume Windows+WSL and would mis-route on macOS — emitting PowerShell-aware advice when the user is in zsh. Cluster G makes the detection work for all three families and delegates the routing rules to user config.

**Completeness check after Cluster G:** Verify no other copilot-native file hardcodes environmental data. `grep -rn "WSL\|PowerShell\|pwsh\|wsl.exe" copilot-native/` should return no matches in shipped skill/prompt/instruction bodies (only in examples/docs is acceptable).

---

## 6. Enhancement Plan — Update Existing Skills

Places where the copilot-native version may carry additions worth merging into the existing `claude/` skill.

| Existing claude skill | Copilot-native counterpart | Candidate enhancement |
|---|---|---|
| `claude/review-adversarial` | `prompts/dev/adversarial-review.prompt.md` | Explicit "switch model family" discipline; cross-model verdict rubric |
| `claude/test-plan` | `skills/test-planning/SKILL.md` | Review the TDD-first rubric for any novel checklist items |
| `claude/review-gauntlet` | `prompts/review/adversarial-review-gauntlet.prompt.md` | Already in parity per `MAPPING.md` — verify no drift |

Action: small diffs, handled as part of Cluster A port (since adversarial-review and review-gauntlet are load-bearing for governed execution).

---

## 7. Items NOT to Port

| Item | Reason |
|---|---|
| `copilot-native/skills/copilot-platform-playbook/` | Copilot-platform-specific design framework. Claude Code has its own authoring patterns. |
| `copilot-native/prompts/dev/copilot-asset-audit.prompt.md` | Copilot-platform-specific asset audit. Claude Code equivalent is `claude/skill-audit` (already exists). |
| `copilot-native/instructions/copilot-asset-authoring.instructions.md` | Copilot-platform-specific authoring rules. |
| BA prompts 1–5 (ba-problem-refiner, ba-spec-engineer, ba-context-builder, ba-eval-harness, ba-knowledge-capture) | Already available as Claude Code plugins. Use plugins. |
| `tech-ideation` skill | Evaluate first — may be redundant with `superpowers:brainstorming`. |
| Agents with direct plugin subagent equivalents (code-reviewer, adversarial-reviewer) | Use plugin subagents. |

---

## 8. Built-in Adoption Recommendations

Where Claude Code built-ins should be preferred over custom canonical skills:

| Workflow | Use built-in | Instead of creating |
|---|---|---|
| Brainstorm a feature | `superpowers:brainstorming` | New skill |
| Write an implementation plan | `superpowers:writing-plans` or `claude/plan` | New planning skill |
| Execute a plan with checkpoints | `superpowers:executing-plans` | New execution skill |
| TDD discipline | `superpowers:test-driven-development` | New TDD skill |
| Debug a failing test | `superpowers:systematic-debugging` | New debug skill |
| Verify completion | `superpowers:verification-before-completion` | Custom verification |
| Code review | `pr-review-toolkit:review-pr` | New review skill |
| BA problem refinement | `ba-problem-refiner` plugin | Port copilot-native BA prompts |
| BA spec engineering | `ba-spec-engineer` plugin | Port copilot-native |
| Commit + push + PR | `commit-commands:commit-push-pr` | New commit skill |
| Isolated branch work | `superpowers:using-git-worktrees` | New worktree skill |
| Parallel subagent tasks | `superpowers:dispatching-parallel-agents` | Custom orchestration |
| Static security analysis | `static-analysis:semgrep` / `codeql` | Custom security skill |

---

## 9. Consolidated List — Files YOU Will Need to Edit

After the port completes, these are the files you (the user) must fill in. The canonical skills ship with blank templates and explicit placeholders; **each config-dependent skill does a pre-flight check and will halt with actionable instructions if you haven't filled them in**. You can fill them in by running `/configure <target>` (recommended) or by hand-editing.

### Per-user global (edit once, applies everywhere)

| File | Why it needs editing | Owner |
|---|---|---|
| `~/.claude/env.config.md` | Your homelab shell/host routing. Ships blank with sections for WSL hosts, macOS hosts, Linux hosts, terminal-switching rules. | Cluster D |
| `~/.claude/CLAUDE.md` | Add 5-line pointer rule referencing `env.config.md`. | Cluster D |
| `~/.claude/code-investigate.config.md` | Default report root, default repo search roots. | Cluster B |

### Per-project (edit once per project that opts in)

| File | Why it needs editing | Owner |
|---|---|---|
| `<project>/.claude/workflow.config.md` | Process doc root + template root + run artifact root for governed workflow. | Cluster A |
| `<project>/docs/process/execute-workflow.md` | Project's execution process doc (content). | Cluster A |
| `<project>/docs/process/review-and-disposition.md` | Project's review+disposition process (content). | Cluster A |
| `<project>/docs/process/evidence-and-artifacts.md` | Project's evidence rules (content). | Cluster A |
| `<project>/docs/process/document-schema.md` | Project's artifact schema (content). | Cluster A |
| `<project>/docs/templates/*.template.md` | Artifact templates for review-plan, review-code, adversarial-review, disposition-log, execution-report, postmortem. | Cluster A |
| `<project>/CLAUDE.md` — ship section | Project's delivery commands (build/test/tag/release/deploy). | Cluster A |

**Note:** process docs + artifact templates above are **Copilot-native's referenced-but-missing** artifacts (see copilot-native/README.md §"Notes on referenced but non-local files"). Porting to Claude will require authoring them once per project — or leaving `claude/execute-workflow` as opt-in for projects that invest the setup cost.

### Per-skill templates (shipped in canonical, copied to user scope)

| Skill | Template shipped | Deployment pattern |
|---|---|---|
| `claude/execute-workflow` | `config.template.md` | User copies to `<project>/.claude/workflow.config.md` and edits. |
| `claude/execute-workflow` | `process-docs.template/` (5 files, A7) | User copies to `<project>/docs/process/` and edits per project. |
| `claude/execute-workflow` | `artifact-templates.template/` (6 files, A8) | User copies to `<project>/docs/templates/` and edits per project. |
| `claude/env-check` | `env.config.template.md` | User copies to `~/.claude/env.config.md` and edits. |
| `claude/code-investigate` | `config.template.md` | User copies to `~/.claude/code-investigate.config.md` and edits. |

### copilot-native (Cluster G — self-heal)

| Template shipped | Deployment pattern |
|---|---|
| `copilot-native/templates/env.config.template.md` | User copies to `$HOME/.copilot/env.config.md` or `<project>/.github/instructions/env.config.md` and edits. |

---

## 10. Proposed Implementation Sequence

Dependency-ordered. Each phase is independently reviewable. **Path A adopted — direct file-level porting.**

### Phase 0 — Configure skill + pre-flight check pattern (enables every config-dependent cluster)
1. `claude/configure` skill + template registry
2. `copilot-native/prompts/common/configure.prompt.md`
3. Document the pre-flight check canonical pattern (as reusable fragment)

### Phase 1 — Foundations (universal, no config needed)
4. `claude/_internal/disposition` (rubric, not user-invokable)
5. `claude/_internal/repo-delivery` (rubric, not user-invokable)
6. `claude/env-check` skill + ship blank `env.config.template.md` + embed pre-flight check
7. Author global `~/.claude/CLAUDE.md` pointer rule (5 lines, references `env.config.md`)

### Phase 2 — Governed execution
8. `claude/execute-workflow` + ship blank `config.template.md` + embed pre-flight check
9. `claude/execute-workflow/process-docs.template/` (5 files, A7)
10. `claude/execute-workflow/artifact-templates.template/` (6 files, A8)
11. `claude/kickoff`
12. `claude/ship` + ship blank `config.template.md` + embed pre-flight check
13. `claude/postmortem` (shares workflow.config.md, same pre-flight)

### Phase 3 — Readiness + investigation
14. `claude/prd-readiness`
15. `claude/prd-validate`
16. `claude/code-investigate` + ship blank `config.template.md` + embed SOFT pre-flight check

### Phase 4 — copilot-native self-heal (Cluster G)
17. Rewrite `copilot-native/skills/execution-environment/SKILL.md` (detection protocol only, embed pre-flight check)
18. Rewrite `copilot-native/instructions/execution-environment.instructions.md` (thin always-on rule)
19. Ship `copilot-native/templates/env.config.template.md` (blank structured template)
20. Edit `copilot-native/prompts/common/environment-check.prompt.md` (strip bake-in)
21. Verify no other copilot-native file hardcodes env data

### Phase 5 — Evaluate + retire
22. Evaluate `claude/ideate` vs `superpowers:brainstorming` — drop or ship
23. Enhance existing `claude/review-adversarial` with model-switch discipline
24. Retire `vscode/` tree and `MAPPING.md` (archive to `archives/`)
25. Retire `deploy.sh` (already deprecated)

### Phase 6 — Completed renames in current Claude structure
26. `claude/prd-acceptance`
27. `claude/dep-audit`
28. `claude/dep-migrate`
29. `claude/k8s-verify`
30. `claude/review-adversarial`
31. Remaining future candidate: `claude/ba-adversarial-review` → `claude/ba-review-adversarial`
32. Keep cross-references aligned with the current names.

**Out of scope for this document:** Actual porting work. This is a plan for review.

**Deployment pipeline note:** `deploy.sh` is deprecated. Deployment is handled by the skill-factory at `~/repos/skill-factory` (v0.5.0). This plan ports files directly into `~/repos/skills/{claude,copilot-native}/` (Path A — traditional authoring). Moving new skills onto factory intent documents is deferred to a separate future effort.

---

## 11. Open Questions — Resolutions

Recorded here for audit trail. Each resolution is reflected in the plan above.

| # | Question | Resolution |
|---|---|---|
| Q1 | Governance fit? | **Port as opt-in.** Default stays `claude/execute-plan`. Heavyweight `claude/execute-workflow` ships for projects that invest in the process-doc setup. |
| Q2 | Subagent strategy? | **Agent tool + skill reference** for most governance agents. **Custom subagents** only for `orchestrator-code-investigation` + `specialist-code-investigation-search` (distinct JSON-contract protocol). |
| Q3 | PRD naming? | **New `claude/prd-readiness`, keep existing `claude/prd-acceptance`.** |
| Q4 | Ideate evaluate vs port? | **Direct port with in-flight evaluation.** Drop if 30-min port reveals `brainstorming` + BA plugin covers it. |
| Q5 | Shell-routing scope? | **Global `~/.claude/CLAUDE.md` with short pointer** to `~/.claude/env.config.md` (separate editable file). Keeps CLAUDE.md lean; shell-map lives where it can be edited without touching CLAUDE.md. |
| Q6 | MAPPING.md scope? | **Retire `MAPPING.md` after port** along with the `vscode/` tree. Going forward only `claude/` and `copilot-native/` are canonical. |

## 12. New Decisions from This Round

| Decision | Impact |
|---|---|
| **Drop `vscode/` support** | `deploy.sh deploy_vscode()` removed. `MAPPING.md` archived. No more VS Code Copilot ports — `copilot-native/` is the single Copilot canonical. |
| **Environment-neutral canon** | No environmental bake-in in canonical skills. All variable data externalized to editable templates. Every skill that needs env data tells the user which file to edit. |
| **Template file conventions** | Three scopes: `~/.claude/` (per-user), `<project>/.claude/` + `<project>/CLAUDE.md` (per-project), `<skill>/config.template.md` (shipped blank). |
| **Ship process-doc templates (item 1)** | Cluster A expanded with A7 (5 process doc templates) + A8 (6 artifact templates). Dramatically lowers Cluster A onramp cost. |
| **Self-heal copilot-native (item 2)** | New Cluster G added. `execution-environment` skill + instruction + prompt rewritten to use detection protocol + user-config pattern. `personal.instructions.md` unchanged (already correct). |
| **Path A — Direct port** | Skills authored by hand in `~/repos/skills/{claude,copilot-native}/`. Skill-factory migration deferred to separate future effort. |
| **Configure skill + pre-flight checks (Cluster H)** | New `/configure <target>` skill interviews user and fills blank templates. Every config-dependent skill embeds a pre-flight check that halts with actionable "run /configure" or "hand-edit" message if config is missing. Ships first (Phase 0) as dependency for all other clusters. |
| **Naming conventions (§13)** | Prefix-grouped names for alphabetical clustering. Short verbs for atomic ops. `_internal/` namespace hides knowledge skills from `/`-menu. `/kickoff` for autonomous dev, `/env-check`, `/code-investigate`. Copilot agents wrap governed flows. 6 deferred renames for existing skills (Phase 6). |

## 13. Naming Conventions & Discoverability

### The problem

Post-port, the `/`-menu will contain 40+ entries. Without naming discipline, the user can't tell "which one starts the governed flow?" or "which review is the meta-review?" from the slash-command list alone.

### Convention rules

**Rule 1 — Short single-verb names for atomic ops (keep existing):**
`/plan`, `/review`, `/ship`, `/hotfix`, `/checkpoint`, `/pr`, `/commit`, `/triage`, `/changelog`, `/ideate`, `/configure`, `/sync-main`, `/teams`

**Rule 2 — Prefix-group related skills for alphabetical clustering:**

| Prefix | Skills in group |
|---|---|
| `execute-*` | `/execute-plan` (existing), `/execute-workflow` (new) |
| `prd-*` | `/prd-readiness` (new), `/prd-validate` (new), `/prd-acceptance` (rename from `/acceptance`) |
| `review-*` | `/review-api`, `/review-db`, `/review-design`, `/review-tests`, `/review-gauntlet`, `/review-adversarial` |
| `ba-*` | `/ba-*` (existing plugin names — 13 skills) |
| `dep-*` | `/dep-audit` (rename), `/dep-migrate` (rename) |
| `k8s-*` | `/k8s-verify` (rename) |
| `code-*` | `/code-review` (rename), `/code-investigate` (new) |
| `test-*` | `/test-plan` |

**Rule 3 — Distinctive short names for major flow entry points:**

| Entry point | Name | Why |
|---|---|---|
| Start from AERS/story (lightweight built-in-first) | **`/kickoff`** | Short, distinctive. NOT `/autonomous-dev`. |
| Execute a written plan (simple) | `/execute-plan` (existing) | Already clear. |
| Governed execution with artifact trail | `/execute-workflow` (new) | Groups with execute-plan. |
| Post-run retrospective | `/postmortem` (new) | Short, universally understood. |

**Rule 4 — Rubric/knowledge skills are NOT in `/`-menu:**

Knowledge rubrics that other skills reference are placed in `claude/_internal/` namespace. They do NOT appear as slash commands and are never user-invoked directly.

| Rubric skill | Path | Referenced by |
|---|---|---|
| disposition | `claude/_internal/disposition/SKILL.md` | execute-workflow, postmortem, kickoff |
| repo-delivery | `claude/_internal/repo-delivery/SKILL.md` | execute-plan, ship, hotfix, checkpoint |
| review-foundations | `claude/_internal/review-foundations/SKILL.md` (future, Cluster F) | review-api, review-db, review-design, review-tests |

**Rule 5 — `/configure` with subcommand-style argument (one command):**
- `/configure` with no arg → list available targets + which are unconfigured
- `/configure env` → set up shell routing
- `/configure workflow` → set up governed workflow in current project
- `/configure ship` → set up delivery commands
- `/configure investigate-code` → set up investigation defaults
- `/configure copilot-env` → set up Copilot shell routing

**Rule 6 — Copilot agents wrap multi-step flows (visible in `/agent` picker):**

| Flow | Copilot prompt (in `/`) | Copilot agent (in `@`) | Claude skill (in `/`) |
|---|---|---|---|
| Governed execution | `/execute-workflow` | `@workflow-orchestrator` | `/execute-workflow` |
| Autonomous kickoff | `/kickoff` | `@workflow-kickoff` | `/kickoff` |
| Code investigation | `/code-investigate` | `@investigation-orchestrator` | `/code-investigate` |
| Postmortem | `/postmortem` | `@postmortem-analyst` | `/postmortem` |
| PRD validation | `/prd-validate` | `@prd-quality-gate` | `/prd-validate` |
| Adversarial review | `/review-adversarial` | `@adversarial-reviewer` | `/review-adversarial` |

### Naming decisions (recorded)

| # | Decision | Resolution |
|---|---|---|
| N1 | Rename `acceptance` → `prd-acceptance`? | **Yes.** Groups the PRD lifecycle together. |
| N2 | `autonomous-dev` name | **`/kickoff`** — short, distinctive, no jargon. |
| N3 | Rubric skills placement | **`_internal/` namespace** — keeps `/`-menu clean, still discoverable by skills that reference them. |
| N4 | `/configure` structure | **One command + target argument** — no separate `/configure-env`, `/configure-workflow`. |
| N5 | Copilot agent wrappers? | **Yes.** Agents wrap governed flow entry points. Prompts are thin launchers; agents do the orchestration. |

### Rename status (existing skills — Phase 6)

These existing `claude/` skill names are now aligned with the prefix-group convention unless noted:

| Current name | Status | Change |
|---|---|---|
| `claude/prd-acceptance` | done | Prefix-group |
| `claude/dep-audit` | done | Shorten prefix |
| `claude/dep-migrate` | done | Shorten + cluster |
| `claude/k8s-verify` | done | Shorten |
| `claude/code-review` | done | Already good |
| `claude/review-adversarial` | done | Cluster-prefix |
| `claude/ba-adversarial-review` | future candidate | Cluster-prefix |
| `claude/env-check` | done | New skill ships as `env-check` |
| `claude/code-investigate` | done | New skill ships as `code-investigate` |

---

## 14. Status — Ready to Port

All scope questions resolved. Path A adopted. Naming conventions adopted. Plan is complete.

**Final cluster count:** 8 clusters, 32 sequenced items across 7 phases.

| Phase | Scope | Item count |
|---|---|---|
| 0 | Configure skill + pre-flight pattern (Cluster H) | 3 |
| 1 | Foundations — `_internal/disposition`, `_internal/repo-delivery`, `env-check` | 4 |
| 2 | Governed execution — `execute-workflow`, process-doc templates, `kickoff`, `ship`, `postmortem` | 6 |
| 3 | Readiness + investigation — `prd-readiness`, `prd-validate`, `code-investigate` | 3 |
| 4 | copilot-native self-heal (Cluster G) | 5 |
| 5 | Evaluate + retire (ideate eval, adversarial-review enhancement, vscode retirement) | 4 |
| 6 | Completed/current rename alignment (prd-acceptance, dep-audit, k8s-verify, etc.) | 7 |

**When ready to start building, invoke me with something like:**

- `"start phase 0"` — I'll author `claude/configure` + `copilot-native/prompts/common/configure.prompt.md` + the template registry
- `"port cluster A"` — I'll author all 8 Cluster A assets in sequence with review checkpoints
- `"port everything through phase 3"` — I'll work through phases 0-3 with a checkpoint between each phase

**What I will do at each port step:**

1. Read the copilot-native source file(s) being ported
2. Strip environmental bake-in (env-neutrality principle)
3. Author the canonical Claude `SKILL.md` or Copilot `.prompt.md`/`.agent.md`/`.skill.md`
4. Embed the pre-flight check pattern if the skill needs config
5. Ship companion template files with `<FILL IN>` placeholders
6. Update `claude/configure/registry.md` with the new target entry
7. Surface to you: "Created X. Pre-flight config: Y. You'll need to run `/configure Y` or edit Z."
