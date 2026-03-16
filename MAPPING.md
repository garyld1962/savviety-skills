# Skills Cross-Platform Mapping

This file maps each skill between Claude Code and VS Code / GitHub Copilot formats.

## Platform Format Reference

| Concept | Claude Code | VS Code / GitHub Copilot |
|---------|-------------|--------------------------|
| User-invokable command | `.claude/skills/<name>/SKILL.md` | `.github/prompts/<name>.prompt.md` |
| Auto-applied rules | `CLAUDE.md` (always loaded) | `.github/instructions/<name>.instructions.md` |
| Repo-wide instructions | `CLAUDE.md` | `.github/copilot-instructions.md` |
| Reusable context | Sub-files in skill dir | `.github/skills/<name>/SKILL.md` |
| Autonomous worker | Agent tool (subagent) | `.github/agents/<name>.agent.md` |

## Skill Mapping Table

Status: `=` in sync, `C>` Claude only, `V>` VS Code only, `~` functionally equivalent but platform-adapted

### Dev Workflow Skills

| Skill | Claude | VS Code | Status | Notes |
|-------|--------|---------|--------|-------|
| plan | `claude/plan/` | `vscode/prompts/dev/plan.prompt.md` | ~ | Claude has existing deployed version |
| execute-plan | `claude/execute-plan/` | `vscode/prompts/dev/execute-plan.prompt.md` | ~ | Claude has existing deployed version |
| hotfix | `claude/hotfix/` | `vscode/prompts/dev/hotfix.prompt.md` | = | New — created in sync |
| triage | `claude/triage/` | `vscode/prompts/dev/triage.prompt.md` | = | New — created in sync |
| changelog | `claude/changelog/` | `vscode/prompts/dev/changelog.prompt.md` | = | New — created in sync |
| work-item | `claude/work-item/` | `vscode/prompts/dev/ado-item.prompt.md` | ~ | Claude supports both ADO + Linear; VS Code is ADO-only |
| simplify | superpowers plugin | `vscode/prompts/dev/simplify.prompt.md` | ~ | Claude uses 3 parallel agents; VS Code is single-pass |
| checkpoint | `claude/checkpoint/` | `vscode/prompts/dev/checkpoint.prompt.md` | ~ | Claude has existing deployed version |
| code-review | `claude/code-review/` | `vscode/prompts/dev/code-review.prompt.md` | ~ | Claude has existing deployed version |
| pr | `claude/pr/` | `vscode/prompts/dev/pr.prompt.md` | ~ | Claude has existing deployed version |
| ship | `claude/ship/` | `vscode/prompts/dev/ship.prompt.md` | ~ | Claude has existing deployed version |
| teams | `claude/teams/` | `vscode/prompts/dev/teams.prompt.md` | ~ | Claude has existing deployed version |
| test-plan | `claude/test-plan/` | — | C> | No VS Code equivalent yet |
| sync-main | `claude/sync-main/` | — | C> | No VS Code equivalent yet |

### Review Skills

| Skill | Claude | VS Code | Status | Notes |
|-------|--------|---------|--------|-------|
| adversarial-review | `claude/adversarial-review/` | `vscode/prompts/dev/adversarial-review.prompt.md` | ~ | Claude uses codex/gemini CLIs; VS Code uses Copilot model switching |
| review-gauntlet | `claude/review-gauntlet/` | `vscode/prompts/review/adversarial-review-gauntlet.prompt.md` | = | New — created in sync |
| review-api | `claude/review-api/` | — | C> | Claude has existing deployed version |
| review-db | `claude/review-db/` | — | C> | Claude has existing deployed version |
| review-design | `claude/review-design/` | — | C> | Claude has existing deployed version |
| review-tests | `claude/review-tests/` | — | C> | Claude has existing deployed version |
| review (file) | — | `vscode/prompts/review/review-file.prompt.md` | V> | |
| review (project) | — | `vscode/prompts/review/review-project.prompt.md` | V> | |
| review (solution) | — | `vscode/prompts/review/review-solution.prompt.md` | V> | |

### BA Skills

| Skill | Claude | VS Code | Status | Notes |
|-------|--------|---------|--------|-------|
| ba-adversarial-review | `claude/ba-adversarial-review/` | `vscode/prompts/ba/ba-adversarial-review.prompt.md` | = | New — created in sync |
| ba-init | superpowers plugin | `vscode/prompts/ba/ba-init.prompt.md` | ~ | Claude version is a superpowers skill |
| ba-context-builder | superpowers plugin | `vscode/prompts/ba/ba-context-builder.prompt.md` | ~ | |
| ba-problem-thesis | superpowers plugin | `vscode/prompts/ba/ba-problem-thesis.prompt.md` | ~ | |
| ba-problem-refiner | superpowers plugin | `vscode/prompts/ba/ba-problem-refiner.prompt.md` | ~ | |
| ba-current-state | superpowers plugin | `vscode/prompts/ba/ba-current-state.prompt.md` | ~ | |
| ba-requirements | superpowers plugin | `vscode/prompts/ba/ba-requirements.prompt.md` | ~ | |
| ba-validation | superpowers plugin | `vscode/prompts/ba/ba-validation.prompt.md` | ~ | |
| ba-solution | superpowers plugin | `vscode/prompts/ba/ba-solution.prompt.md` | ~ | |
| ba-stakeholder | superpowers plugin | `vscode/prompts/ba/ba-stakeholder.prompt.md` | ~ | |
| ba-preflight | superpowers plugin | `vscode/prompts/ba/ba-preflight.prompt.md` | ~ | |
| ba-eval-harness | superpowers plugin | `vscode/prompts/ba/ba-eval-harness.prompt.md` | ~ | |
| ba-knowledge-capture | superpowers plugin | `vscode/prompts/ba/ba-knowledge-capture.prompt.md` | ~ | |
| ba-spec-engineer | superpowers plugin | `vscode/prompts/ba/ba-spec-engineer.prompt.md` | ~ | |
| ba-constraint-architecture | — | `vscode/prompts/ba/ba-constraint-architecture.prompt.md` | V> | |

### Technology Skills

| Skill | Claude | VS Code | Status | Notes |
|-------|--------|---------|--------|-------|
| typescript-advanced-types | `claude/typescript-advanced-types/` | — | C> | Existing deployed |
| next-best-practices | `claude/next-best-practices/` | — | C> | Existing deployed |
| vercel-composition-patterns | `claude/vercel-composition-patterns/` | — | C> | Existing deployed |
| vercel-react-best-practices | `claude/vercel-react-best-practices/` | — | C> | Existing deployed |
| agent-browser | `claude/agent-browser/` | `vscode/prompts/common/agent-browser.prompt.md` | ~ | |

### Utility / Common

| Skill | Claude | VS Code | Status | Notes |
|-------|--------|---------|--------|-------|
| find-skills | `claude/find-skills/` | — | C> | Claude-specific discovery |
| setup-common-prompts | — | `vscode/prompts/common/setup-common-prompts.prompt.md` | V> | VS Code setup helper |

### VS Code Only — Agents

These have no direct Claude equivalent (Claude uses the Agent tool with subagent_type instead):

| Agent | File | Purpose |
|-------|------|---------|
| architecture-mapper | `vscode/agents/architecture-mapper.agent.md` | Maps codebase architecture |
| async-safety | `vscode/agents/async-safety.agent.md` | Async/await pattern review |
| code-review-orchestrator | `vscode/agents/code-review-orchestrator.agent.md` | Orchestrates multi-specialist review |
| complexity | `vscode/agents/complexity.agent.md` | Complexity analysis |
| csharp-quality | `vscode/agents/csharp-quality.agent.md` | C# quality review |
| di-architecture | `vscode/agents/di-architecture.agent.md` | DI pattern review |
| k8s-readiness | `vscode/agents/k8s-readiness.agent.md` | Kubernetes readiness review |
| review-report-writer | `vscode/agents/review-report-writer.agent.md` | Formats review reports |
| security | `vscode/agents/security.agent.md` | Security review |

### VS Code Only — Instructions (auto-applied by path)

| Instruction | File | Applies To |
|-------------|------|-----------|
| DOCX processing | `vscode/instructions/docx-processing.instructions.md` | `*.docx` files |
| PDF processing | `vscode/instructions/pdf-processing.instructions.md` | `*.pdf` files |
| PDF forms | `vscode/instructions/pdf-forms.instructions.md` | `*.pdf` form files |
| PPTX processing | `vscode/instructions/pptx-processing.instructions.md` | `*.pptx` files |
| XLSX processing | `vscode/instructions/xlsx-processing.instructions.md` | `*.xlsx` files |

### VS Code Only — Skills (reusable context for agents)

| Skill | File | Purpose |
|-------|------|---------|
| api-patterns | `vscode/skills/api-patterns/SKILL.md` | API design patterns reference |
| architecture-map | `vscode/skills/architecture-map/SKILL.md` | Architecture mapping reference |
| async-safety | `vscode/skills/async-safety/SKILL.md` | Async safety patterns |
| ba-templates | `vscode/skills/ba-templates/` | BA document templates |
| code-review-orchestrator | `vscode/skills/code-review-orchestrator/SKILL.md` | Review orchestration reference |
| complexity | `vscode/skills/complexity/SKILL.md` | Complexity metrics reference |
| csharp-quality | `vscode/skills/csharp-quality/SKILL.md` | C# quality rules |
| di-architecture | `vscode/skills/di-architecture/SKILL.md` | DI architecture patterns |
| k8s-readiness | `vscode/skills/k8s-readiness/SKILL.md` | K8s readiness checklist |
| review-foundations | `vscode/skills/review-foundations/` | Review rubrics, schemas, templates |
| review-report-writer | `vscode/skills/review-report-writer/SKILL.md` | Report formatting reference |
| security | `vscode/skills/security/SKILL.md` | Security review checklist |
| team-roles | `vscode/skills/team-roles/` | Team role definitions |
| test-quality | `vscode/skills/test-quality/SKILL.md` | Test quality criteria |
| typescript-quality | `vscode/skills/typescript-quality/SKILL.md` | TypeScript quality rules |
| ui-design-compliance | `vscode/skills/ui-design-compliance/SKILL.md` | UI design compliance checks |

## Maintenance Workflow

1. **Edit in this repo** — make changes under `claude/` or `vscode/` as appropriate
2. **Run `./deploy.sh`** — copies to consumption points
3. **Update this table** — if adding, removing, or changing mapping status
4. **Test** — open Claude Code or VS Code in a project and verify the skill loads
