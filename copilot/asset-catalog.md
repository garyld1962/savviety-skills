# Copilot-Native Asset Catalog

This document is a file-by-file guide to the `copilot-native/` workspace. It covers the prompts, agents, skills, instructions, and the top-level files that shape how those assets are intended to work together.

## What this folder is

`copilot-native/` is a staging area for a **built-in-first GitHub Copilot architecture**. The basic split is:

| Asset type | Source path in this repo | Intended deployed path | Role |
|---|---|---|---|
| Prompts | `copilot-native/prompts/**` | `.github/prompts/**` | User-invokable workflows |
| Agents | `copilot-native/agents/*.agent.md` | `.github/agents/*.agent.md` | Narrow specialist workers |
| Skills | `copilot-native/skills/*/SKILL.md` | `.github/skills/*/SKILL.md` | Durable rubrics, heuristics, and workflow knowledge |
| Instructions | `copilot-native/instructions/*.instructions.md` | `.github/instructions/*.instructions.md` | Passive always-on rules |
| Repo instructions | `copilot-native/copilot-instructions.md` | `.github/copilot-instructions.md` | Project-level source of truth |

## Inventory snapshot

| Group | Count | Notes |
|---|---:|---|
| Prompts | 47 | 8 BA, 2 common, 28 dev, 9 review |
| Agents | 12 | Mostly bounded review, ideation, execution, and investigation roles |
| Skills | 27 | Reusable knowledge used by prompts and agents |
| Instructions | 3 | Passive authoring, environment, and personal rule layers |
| Templates | 1 | Blank config template currently shipped for Copilot-side environment routing |

Ignore the `:Zone.Identifier` sidecar files in this folder. They are Windows metadata, not Copilot assets.

## Top-level control files

| File | Purpose |
|---|---|
| [README.md](README.md) | Main overview for the workspace: why it exists, design principles, current asset set, and the intended shared/project/local layout. |
| [platform-review.md](platform-review.md) | Strategy note describing the move toward a more Copilot-native, built-in-first architecture. |
| [copilot-instructions.md](copilot-instructions.md) | Project instruction template and intended single source of truth for conventions, build/test commands, environment model, and AERS expectations. |
| [templates/env.config.template.md](templates/env.config.template.md) | Blank environment-routing template intended to be copied into a user or project Copilot config location. |

## Major workflow clusters

### BA and requirements shaping

The BA prompt set centers on refinement and context capture:

- prompts in `prompts/ba/`
- skills `prd-readiness`, `project-context`, `ba-knowledge-ops`, `ba-ideation`, and `tech-ideation`
- agents `ba-ideation.agent.md` and `prd-quality-gate.agent.md`

The BA set also includes `ubiquitous-language`, a glossary-building prompt for locking in domain terms before planning or implementation.

### Governed execution and delivery

The governed-delivery path combines:

- prompts such as `autonomous-development-kickoff`, `execute-plan`, `execute-workflow`, `modernize`, `checkpoint`, `ship`, `hotfix`, and `postmortem`
- agents such as `execute-orchestrator`, `plan-reviewer`, `code-reviewer`, `adversarial-reviewer`, `disposition-coordinator`, and `postmortem-analyst`
- skills such as `repo-delivery`, `review-disposition-governance`, `execution-environment`, and `copilot-platform-playbook`

Several of these assets also reference process and template files under `.github/docs/process/` and `.github/docs/templates/`. Those paths are part of the intended deployed workspace contract; there are no matching source files under `copilot-native/` today.

### Code investigation

The investigation workflow is a distinct cluster:

- prompt `prompts/dev/investigate-code.prompt.md`
- agents `orchestrator-code-investigation`, `specialist-code-investigation-search`, and `writer-investigation-report`
- skills `code-investigation-orchestrator`, `code-investigation-search`, and `investigation-report-writer`

This cluster is designed to write reports under `docs/code-investigations/`.

### Prompt discovery and configuration

Two lighter support prompts improve day-to-day ergonomics around the rest of the asset set:

- `prompts/common/configure.prompt.md` for filling shipped config templates such as the Copilot environment template
- `prompts/dev/skill-help.prompt.md` for browsing the prompt surface and getting per-prompt help

### Specialist review

The specialist review path is intentionally thinner than a general `/review`:

- prompts `review-api`, `review-db`, `review-design`, `review-tests`
- base skill `review-foundations`
- domain skills `api-patterns`, `db-schema-review`, `ui-design-compliance`, and `test-quality`
- separate adversarial-review assets for second-opinion challenge passes

## Prompt catalog

### BA prompts

| Prompt | File | Purpose | Main related assets |
|---|---|---|---|
| `ba-context-builder` | [prompts/ba/ba-context-builder.prompt.md](prompts/ba/ba-context-builder.prompt.md) | Build a reusable BA project context document for later sessions. | `project-context` |
| `ba-eval-harness` | [prompts/ba/ba-eval-harness.prompt.md](prompts/ba/ba-eval-harness.prompt.md) | Design a repeatable evaluation suite for AI-generated BA deliverables. | `ba-knowledge-ops` |
| `ba-knowledge-capture` | [prompts/ba/ba-knowledge-capture.prompt.md](prompts/ba/ba-knowledge-capture.prompt.md) | Capture decisions, stakeholder intelligence, and lessons learned in a reusable format. | `ba-knowledge-ops` |
| `ba-problem-refiner` | [prompts/ba/ba-problem-refiner.prompt.md](prompts/ba/ba-problem-refiner.prompt.md) | Refine a vague business problem into a precise solution-neutral statement. | `prd-readiness` |
| `ba-spec-engineer` | [prompts/ba/ba-spec-engineer.prompt.md](prompts/ba/ba-spec-engineer.prompt.md) | Build an execution-ready BA specification or AERS through structured interview. | `prd-readiness` |
| `ideate` | [prompts/ba/ideate.prompt.md](prompts/ba/ideate.prompt.md) | Explore and shape an idea for mixed business and technical audiences. | `ba-ideation`, `tech-ideation`, `ba-ideation.agent.md`, `tech-ideation.agent.md` |
| `prd-validator` | [prompts/ba/prd-validator.prompt.md](prompts/ba/prd-validator.prompt.md) | Turn a rough story, BRD, or draft AERS into an implementation-ready artifact. | `prd-readiness`, `prd-quality-gate.agent.md` |
| `ubiquitous-language` | [prompts/ba/ubiquitous-language.prompt.md](prompts/ba/ubiquitous-language.prompt.md) | Build or refresh a domain glossary with canonical terms, aliases to avoid, and unresolved terminology risks. | BA/discovery workflows |

### Common prompts

| Prompt | File | Purpose | Main related assets |
|---|---|---|---|
| `configure` | [prompts/common/configure.prompt.md](prompts/common/configure.prompt.md) | Fill in shipped config templates and write the result to the correct user or project location. | `templates/env.config.template.md`, `execution-environment` |
| `environment-check` | [prompts/common/environment-check.prompt.md](prompts/common/environment-check.prompt.md) | Detect whether commands should run in PowerShell, WSL/Linux, or after a terminal switch. | `execution-environment`, `execution-environment.instructions.md` |

### Dev prompts

| Prompt | File | Purpose | Main related assets |
|---|---|---|---|
| `ado-item` | [prompts/dev/ado-item.prompt.md](prompts/dev/ado-item.prompt.md) | Retrieve and normalize an Azure DevOps work item for downstream workflows. | `ado-work-items` |
| `adversarial-review` | [prompts/dev/adversarial-review.prompt.md](prompts/dev/adversarial-review.prompt.md) | Run a cross-model challenge review and persist the result. | `adversarial-review`, `adversarial-reviewer.agent.md` |
| `autonomous-development-kickoff` | [prompts/dev/autonomous-development-kickoff.prompt.md](prompts/dev/autonomous-development-kickoff.prompt.md) | Start autonomous development from a repo ask, story, or PRD using a built-in-first flow. | `copilot-platform-playbook`, `execution-environment`, `prd-readiness`, `prd-quality-gate.agent.md`, `adversarial-review.prompt.md` |
| `checkpoint` | [prompts/dev/checkpoint.prompt.md](prompts/dev/checkpoint.prompt.md) | Run the repo's real lint/build/test quality gate over the changed scope. | `repo-delivery`, `execution-environment` |
| `copilot-asset-audit` | [prompts/dev/copilot-asset-audit.prompt.md](prompts/dev/copilot-asset-audit.prompt.md) | Audit a Copilot asset set for duplication, missing structure, and modernization opportunities. | `copilot-platform-playbook`, `copilot-asset-authoring.instructions.md` |
| `dependency-audit` | [prompts/dev/dependency-audit.prompt.md](prompts/dev/dependency-audit.prompt.md) | Audit dependency health, security, outdated packages, and license posture. | `dependency-change-management` |
| `execute-plan` | [prompts/dev/execute-plan.prompt.md](prompts/dev/execute-plan.prompt.md) | Execute an accepted plan in dependency order with repo-real commands. | `repo-delivery`, `execution-environment` |
| `execute-workflow` | [prompts/dev/execute-workflow.prompt.md](prompts/dev/execute-workflow.prompt.md) | Run the full governed execution workflow from a requirements artifact. | `copilot-platform-playbook`, `execution-environment`, `prd-readiness`, `review-disposition-governance`, `execute-orchestrator.agent.md`, workflow docs/templates |
| `hotfix` | [prompts/dev/hotfix.prompt.md](prompts/dev/hotfix.prompt.md) | Apply a minimal fast-tracked production fix with tight scope control. | `repo-delivery`, `execution-environment` |
| `investigate-code` | [prompts/dev/investigate-code.prompt.md](prompts/dev/investigate-code.prompt.md) | Search one or more repos for a behavior or pattern and write a Markdown report. | `code-investigation-orchestrator`, `code-investigation-search`, `investigation-report-writer`, investigation agents |
| `k8s-deploy-verify` | [prompts/dev/k8s-deploy-verify.prompt.md](prompts/dev/k8s-deploy-verify.prompt.md) | Verify Kubernetes rollouts, pod health, endpoints, events, and optional logs. | `k8s-verification`, `execution-environment` |
| `migration-guide` | [prompts/dev/migration-guide.prompt.md](prompts/dev/migration-guide.prompt.md) | Produce a repo-specific major-version migration guide. | `dependency-change-management` |
| `modernize` | [prompts/dev/modernize.prompt.md](prompts/dev/modernize.prompt.md) | Audit an older codebase and emit a within-stack refactor plan shaped for `execute-prd --type=refactor`. | `modernization-rubric`, `copilot-platform-playbook` |
| `postmortem` | [prompts/dev/postmortem.prompt.md](prompts/dev/postmortem.prompt.md) | Run a governed postmortem over a completed execution run. | `copilot-platform-playbook`, `review-disposition-governance`, `postmortem-analyst.agent.md`, workflow docs/templates |
| `ship` | [prompts/dev/ship.prompt.md](prompts/dev/ship.prompt.md) | Move completed work through the repo's actual delivery flow. | `repo-delivery`, `execution-environment` |
| `skill-help` | [prompts/dev/skill-help.prompt.md](prompts/dev/skill-help.prompt.md) | Discover available prompts and show concise help for one prompt by name. | prompt discovery ergonomics |
| `test-plan` | [prompts/dev/test-plan.prompt.md](prompts/dev/test-plan.prompt.md) | Create or refresh a repo-specific TDD-first test plan. | `test-planning` |

### Review prompts

| Prompt | File | Purpose | Main related assets |
|---|---|---|---|
| `adversarial-review-gauntlet` | [prompts/review/adversarial-review-gauntlet.prompt.md](prompts/review/adversarial-review-gauntlet.prompt.md) | Challenge review output itself from one or more adversarial lenses. | `adversarial-review`, `adversarial-reviewer.agent.md` |
| `domain-review` | [prompts/review/domain-review.prompt.md](prompts/review/domain-review.prompt.md) | Run the structured defect-focused review lane when built-in `/review` is not enough. | `review-engine` |
| `professional-review` | [prompts/review/professional-review.prompt.md](prompts/review/professional-review.prompt.md) | Run the senior-bar engineering judgment lane for scale, failure, operations, and design quality. | `review-engine` |
| `review-api` | [prompts/review/review-api.prompt.md](prompts/review/review-api.prompt.md) | Run a targeted backend/service review backed by the shared review engine. | `review-engine`, `api-patterns` |
| `review-db` | [prompts/review/review-db.prompt.md](prompts/review/review-db.prompt.md) | Run a targeted database review backed by the shared review engine. | `review-engine`, `db-schema-review` |
| `review-design` | [prompts/review/review-design.prompt.md](prompts/review/review-design.prompt.md) | Run a targeted UI and accessibility review backed by the shared review engine. | `review-engine`, `ui-design-compliance` |
| `review-tests` | [prompts/review/review-tests.prompt.md](prompts/review/review-tests.prompt.md) | Run a targeted test-quality review backed by the shared review engine. | `review-engine`, `test-quality` |

## Agent catalog

| Agent | File | Purpose | Main related assets |
|---|---|---|---|
| `adversarial-reviewer` | [agents/adversarial-reviewer.agent.md](agents/adversarial-reviewer.agent.md) | Perform the skeptical second-pass review and write `adversarial-review.md`. | `adversarial-review.prompt.md`, `review-disposition-governance`, workflow docs/templates |
| `ba-ideation` | [agents/ba-ideation.agent.md](agents/ba-ideation.agent.md) | Facilitate ideation for mixed business and technical audiences. | `ba-ideation` |
| `code-reviewer` | [agents/code-reviewer.agent.md](agents/code-reviewer.agent.md) | Perform the defect-focused domain-review lane for a governed run and write `review-code.md`. | `review-disposition-governance`, workflow docs/templates |
| `disposition-coordinator` | [agents/disposition-coordinator.agent.md](agents/disposition-coordinator.agent.md) | Reconcile review findings into a disposition log. | `review-disposition-governance`, workflow docs/templates |
| `execute-orchestrator` | [agents/execute-orchestrator.agent.md](agents/execute-orchestrator.agent.md) | Orchestrate the governed execution workflow and produce the execution report. | `execute-workflow.prompt.md`, `review-disposition-governance`, workflow docs/templates |
| `orchestrator-code-investigation` | [agents/orchestrator-code-investigation.agent.md](agents/orchestrator-code-investigation.agent.md) | Coordinate cross-repository code investigations and dispatch search/report workers. | `code-investigation-orchestrator`, investigation worker agents |
| `plan-reviewer` | [agents/plan-reviewer.agent.md](agents/plan-reviewer.agent.md) | Review implementation plans for readiness and proof obligations. | `prd-readiness`, `review-disposition-governance`, workflow docs/templates |
| `postmortem-analyst` | [agents/postmortem-analyst.agent.md](agents/postmortem-analyst.agent.md) | Analyze a completed run and write a structured `postmortem.md`. | `postmortem.prompt.md`, `copilot-platform-playbook`, `review-disposition-governance`, workflow docs/templates |
| `prd-quality-gate` | [agents/prd-quality-gate.agent.md](agents/prd-quality-gate.agent.md) | Check an AERS, BRD, or story for execution readiness and ambiguity. | `prd-readiness` |
| `specialist-code-investigation-search` | [agents/specialist-code-investigation-search.agent.md](agents/specialist-code-investigation-search.agent.md) | Search one repository and return structured investigation matches only. | `code-investigation-search` |
| `tech-ideation` | [agents/tech-ideation.agent.md](agents/tech-ideation.agent.md) | Facilitate technical ideation from a rough ask or document set. | `tech-ideation` |
| `writer-investigation-report` | [agents/writer-investigation-report.agent.md](agents/writer-investigation-report.agent.md) | Convert structured investigation results into a versioned Markdown report. | `investigation-report-writer` |

## Skill catalog

| Skill | File | Purpose |
|---|---|---|
| `ado-work-items` | [skills/ado-work-items/SKILL.md](skills/ado-work-items/SKILL.md) | Retrieval and normalization workflow for Azure DevOps work items. |
| `adversarial-review` | [skills/adversarial-review/SKILL.md](skills/adversarial-review/SKILL.md) | Cross-model code review rubric for skeptic, architect, and minimalist challenge passes. |
| `api-patterns` | [skills/api-patterns/SKILL.md](skills/api-patterns/SKILL.md) | Backend/service review rubric for validation, auth, logging, shared types, and operational correctness. |
| `ba-ideation` | [skills/ba-ideation/SKILL.md](skills/ba-ideation/SKILL.md) | Business-analysis ideation workflow for turning rough asks into workshop-ready outputs. |
| `ba-knowledge-ops` | [skills/ba-knowledge-ops/SKILL.md](skills/ba-knowledge-ops/SKILL.md) | Templates and quality checks for BA knowledge capture and BA deliverable evaluation. |
| `code-investigation-orchestrator` | [skills/code-investigation-orchestrator/SKILL.md](skills/code-investigation-orchestrator/SKILL.md) | Orchestration contract for cross-repository code investigations. |
| `code-investigation-search` | [skills/code-investigation-search/SKILL.md](skills/code-investigation-search/SKILL.md) | Search contract and JSON match schema for one-repo investigation workers. |
| `copilot-platform-playbook` | [skills/copilot-platform-playbook/SKILL.md](skills/copilot-platform-playbook/SKILL.md) | Built-in-first design framework for prompts, agents, skills, and instructions. |
| `db-schema-review` | [skills/db-schema-review/SKILL.md](skills/db-schema-review/SKILL.md) | Database schema and migration review rubric. |
| `dependency-change-management` | [skills/dependency-change-management/SKILL.md](skills/dependency-change-management/SKILL.md) | Evidence-based guidance for dependency audits and major-version migrations. |
| `execution-environment` | [skills/execution-environment/SKILL.md](skills/execution-environment/SKILL.md) | Shell and environment detection guidance for PowerShell, WSL, and Linux repos. |
| `investigation-report-writer` | [skills/investigation-report-writer/SKILL.md](skills/investigation-report-writer/SKILL.md) | Formatting and file rules for versioned code-investigation reports. |
| `k8s-verification` | [skills/k8s-verification/SKILL.md](skills/k8s-verification/SKILL.md) | Post-deploy Kubernetes verification checklist. |
| `modernization-rubric` | [skills/modernization-rubric/SKILL.md](skills/modernization-rubric/SKILL.md) | Calibration rubric for modernization audits: project shape, sample-read strategy, admissible moves, and cull criteria. |
| `prd-readiness` | [skills/prd-readiness/SKILL.md](skills/prd-readiness/SKILL.md) | Interactive checklist for turning a story, BRD, or draft AERS into an implementation-ready artifact. |
| `project-context` | [skills/project-context/SKILL.md](skills/project-context/SKILL.md) | Structured interview and output shape for reusable BA project context documents. |
| `repo-delivery` | [skills/repo-delivery/SKILL.md](skills/repo-delivery/SKILL.md) | Delivery playbook for execution, checkpointing, shipping, and hotfixes. |
| `review-disposition-governance` | [skills/review-disposition-governance/SKILL.md](skills/review-disposition-governance/SKILL.md) | Governance rules for plan review, code review, adversarial review, and finding disposition. |
| `review-engine` | [skills/review-engine/SKILL.md](skills/review-engine/SKILL.md) | Shared domain-based review controller and profile library for `domain-review` and `professional-review`. |
| `review-foundations` | [skills/review-foundations/SKILL.md](skills/review-foundations/SKILL.md) | Compatibility bridge for specialist review prompts that now route into the shared review engine. |
| `tech-ideation` | [skills/tech-ideation/SKILL.md](skills/tech-ideation/SKILL.md) | Technical ideation workflow for exploring architecture and systems options without jumping to implementation. |
| `test-planning` | [skills/test-planning/SKILL.md](skills/test-planning/SKILL.md) | TDD-first rubric for generating or refreshing test plans. |
| `test-quality` | [skills/test-quality/SKILL.md](skills/test-quality/SKILL.md) | Test review rubric for coverage quality, async correctness, isolation, and naming. |
| `ui-design-compliance` | [skills/ui-design-compliance/SKILL.md](skills/ui-design-compliance/SKILL.md) | UI review rubric for design-system consistency, accessibility, and theme-safe implementation. |

## Instruction catalog

| Instruction | File | Purpose |
|---|---|---|
| `copilot-asset-authoring` | [instructions/copilot-asset-authoring.instructions.md](instructions/copilot-asset-authoring.instructions.md) | Author prompts, agents, skills, and instructions in a built-in-first style without duplicating Copilot platform features. |
| `execution-environment` | [instructions/execution-environment.instructions.md](instructions/execution-environment.instructions.md) | Apply cross-shell routing rules before suggesting commands or scripts. |
| `personal` | [instructions/personal.instructions.md](instructions/personal.instructions.md) | Local preference layer intended to survive shared asset sync. |

## Notes on referenced but non-local files

The governed execution assets repeatedly reference these deployed paths:

- `.github/docs/process/execute-workflow.md`
- `.github/docs/process/review-and-disposition.md`
- `.github/docs/process/evidence-and-artifacts.md`
- `.github/docs/process/document-schema.md`
- `.github/docs/process/postmortem-workflow.md`
- `.github/docs/templates/*.template.md`

Those references matter because they define the expected run artifacts and output formats for review, execution, disposition, and postmortem flows, even though source files for them are not currently stored under `copilot-native/`.

The workspace also ships one local source template under `templates/`:

- `templates/env.config.template.md`

That file is intended to be copied into `$HOME/.copilot/env.config.md` or `<project>/.github/instructions/env.config.md`. In consuming repos, treat `.github/templates/` as the natural home for shared config templates when the publish pipeline deploys them.
