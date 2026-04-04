# Copilot-Native Workspace

Experimental GitHub Copilot assets designed to be **Copilot-first**, not just Claude ports.

This folder is intentionally separate from `vscode/` so we can explore a better architecture without destabilizing the current deployed prompt set.

## Why this exists

The existing `vscode/` tree is already strong, but much of it mirrors Claude-era workflow commands one-for-one. GitHub Copilot has a different platform shape:

- built-in slash commands like `/plan`, `/review`, `/research`, `/tasks`, `/delegate`, `/agent`, `/skills`, `/instructions`
- project agents and reusable skills
- auto-applied instructions
- background task management
- file mentions and repo context controls

The goal here is to build a thinner, more native layer that:

- uses Copilot built-ins first
- adds custom prompts only where they create real leverage
- keeps domain knowledge in skills
- keeps passive rules in instructions
- uses agents for specialized, bounded roles

## Design principles

1. **Built-in first**
   - Use Copilot built-ins when the platform already solves the problem well.
   - Example: prefer `/plan` for implementation planning and `/review` for default review flows.

2. **Custom prompts for missing workflows**
   - Add prompts for repeatable workflows Copilot does not provide out of the box.
   - Example: `prd-validator` for converting a business problem statement or business PRD into an AERS.

3. **Skills hold durable knowledge**
   - Rubrics, checklists, heuristics, and domain rules belong in skills.
   - Prompts should stay thin and reference skills.

4. **Instructions hold passive invariants**
   - Always-on rules belong in instructions, not duplicated in every prompt.

5. **Agents stay narrow**
   - Agents should have crisp roles with bounded output, not act as generic replacements for the base model.

## Built-in feature strategy

| Copilot built-in | Preferred use in this workspace |
|------------------|---------------------------------|
| `/plan` | default planning path |
| `/review` | default quick code review |
| `/research` | broad repo/web investigation |
| `/tasks` | monitor background work |
| `/delegate` | only when the user explicitly wants cloud execution / PR creation |
| `/agent` | discover/select specialist agents |
| `/skills` | manage installed skills |
| `/instructions` | inspect active instruction layers |
| `/model` | switch models for adversarial or second-opinion passes |
| `@file` mentions | targeted context instead of long pasted prompts |

## Current asset set

### Prompts

- `prompts/ba/ideate.prompt.md`
- `prompts/ba/prd-validator.prompt.md`
- `prompts/ba/ba-problem-refiner.prompt.md`
- `prompts/ba/ba-spec-engineer.prompt.md`
- `prompts/ba/ba-context-builder.prompt.md`
- `prompts/ba/ba-eval-harness.prompt.md`
- `prompts/ba/ba-knowledge-capture.prompt.md`
- `prompts/common/environment-check.prompt.md`
- `prompts/dev/adversarial-review.prompt.md`
- `prompts/dev/autonomous-development-kickoff.prompt.md`
- `prompts/dev/copilot-asset-audit.prompt.md`
- `prompts/dev/execute-plan.prompt.md`
- `prompts/dev/checkpoint.prompt.md`
- `prompts/dev/execute-workflow.prompt.md`
- `prompts/dev/investigate-code.prompt.md`
- `prompts/dev/k8s-deploy-verify.prompt.md`
- `prompts/dev/ship.prompt.md`
- `prompts/dev/hotfix.prompt.md`
- `prompts/dev/postmortem.prompt.md`
- `prompts/dev/test-plan.prompt.md`
- `prompts/dev/migration-guide.prompt.md`
- `prompts/dev/dependency-audit.prompt.md`
- `prompts/dev/ado-item.prompt.md`
- `prompts/review/adversarial-review-gauntlet.prompt.md`
- `prompts/review/review-api.prompt.md`
- `prompts/review/review-db.prompt.md`
- `prompts/review/review-design.prompt.md`
- `prompts/review/review-tests.prompt.md`

### Skills

- `skills/adversarial-review/SKILL.md`
- `skills/ba-ideation/SKILL.md`
- `skills/prd-readiness/SKILL.md`
- `skills/project-context/SKILL.md`
- `skills/ba-knowledge-ops/SKILL.md`
- `skills/code-investigation-orchestrator/SKILL.md`
- `skills/code-investigation-search/SKILL.md`
- `skills/execution-environment/SKILL.md`
- `skills/investigation-report-writer/SKILL.md`
- `skills/review-disposition-governance/SKILL.md`
- `skills/repo-delivery/SKILL.md`
- `skills/k8s-verification/SKILL.md`
- `skills/dependency-change-management/SKILL.md`
- `skills/tech-ideation/SKILL.md`
- `skills/test-planning/SKILL.md`
- `skills/ado-work-items/SKILL.md`
- `skills/review-foundations/SKILL.md`
- `skills/api-patterns/SKILL.md`
- `skills/db-schema-review/SKILL.md`
- `skills/ui-design-compliance/SKILL.md`
- `skills/test-quality/SKILL.md`
- `skills/copilot-platform-playbook/SKILL.md`

### Other assets

- `agents/ba-ideation.agent.md`
- `agents/adversarial-reviewer.agent.md`
- `agents/code-reviewer.agent.md`
- `agents/disposition-coordinator.agent.md`
- `agents/execute-orchestrator.agent.md`
- `agents/orchestrator-code-investigation.agent.md`
- `agents/plan-reviewer.agent.md`
- `agents/postmortem-analyst.agent.md`
- `agents/prd-quality-gate.agent.md`
- `agents/specialist-code-investigation-search.agent.md`
- `agents/tech-ideation.agent.md`
- `agents/writer-investigation-report.agent.md`
- `.github/docs/process/*.md`
- `.github/docs/templates/*.template.md`
- `instructions/copilot-asset-authoring.instructions.md`
- `instructions/execution-environment.instructions.md`
- `instructions/personal.instructions.md`

## Proposed usage model

- Use built-in `/plan` instead of creating another custom planning prompt unless the repo needs special orchestration.
- Use `prd-validator` before planning when the source artifact is still business-oriented, incomplete, or not yet an AERS.
- Use BA prompts like `ba-problem-refiner`, `ba-spec-engineer`, `ba-context-builder`, `ba-eval-harness`, and `ba-knowledge-capture` when the missing piece is business precision or durable context, not implementation orchestration.
- Use `ideate` when the work is still exploratory and you need shared, BA, or technical option-shaping before `/plan`.
- Use `environment-check` when a repo must support both PowerShell and WSL execution patterns.
- Use built-in `/model` and then `adversarial-review` when you want a deliberate second-opinion code challenge instead of the default `/review` path.
- Use `adversarial-review-gauntlet` when the thing you need to challenge is the review output itself, not the code.
- Use `autonomous-development-kickoff` when you want a thin built-in-first path from requirements readiness into `/plan`, implementation, and `/review`.
- Use `execute-workflow` when the work needs governed execution artifacts, required review gates, and explicit disposition handling.
- Use `execute-plan`, `checkpoint`, `ship`, and `hotfix` for repo-specific delivery flows that built-in Copilot does not model directly.
- Use `dependency-audit`, `migration-guide`, and `ado-item` when the workflow depends on repo-local dependency state or external Azure DevOps context.
- Use `investigate-code` when you need an evidence-backed index of where a behavior or API appears across one repo, several repos, or a repo folder.
- Use `postmortem` after a governed run when you want a structured process retrospective tied to the run artifacts.
- Use `review-api`, `review-db`, `review-design`, and `review-tests` when you want narrow compliance checks rather than the broader default `/review`.
- Use `copilot-asset-audit` when reviewing or porting prompt/agent/skill/instruction sets.
- Use the platform playbook skill when authoring new Copilot assets.

## Shared vs local asset convention

For teams using `copilot-native/`, keep three layers distinct:

### Shared canonical layer

These shared assets come from the central repo and are safe to update from
upstream:

- `.github/prompts/ba/`
- `.github/prompts/common/`
- `.github/prompts/dev/`
- `.github/prompts/review/`
- `.github/docs/process/`
- `.github/docs/templates/`
- `.github/skills/<shared-skill>/`
- `.github/agents/`
- `.github/instructions/*.instructions.md`

### Project-owned custom layer

When a specific application repo needs committed custom assets, place them in
reserved project namespaces:

- `.github/prompts/project/`
- `.github/skills/project-<domain>/`
- `.github/agents/project-<name>.agent.md`
- `.github/instructions/project.instructions.md`

### User-local preserved layer

When an individual wants local-only customizations that survive upstream syncs,
use:

- `.github/prompts/local/`
- `.github/skills/local-<user>/`
- `.github/agents/local-<user>.agent.md`
- `.github/instructions/personal.instructions.md`

For cross-project personal preferences, use Copilot CLI’s user-level
instruction locations:

- `$HOME/.copilot/copilot-instructions.md`
- `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`

### Preservation rule

Any deploy/sync process should overwrite only the shared canonical layer and
must never overwrite:

- `.github/instructions/personal.instructions.md`
- `.github/prompts/local/**`
- `.github/skills/local-*/**`
- `.github/agents/local-*.agent.md`

## `vscode/` workflows still not ported here

The lower-priority `vscode/` workflows still left behind are mostly the ones
that already have a credible built-in Copilot counterpart or are still too
portfolio-specific to justify native migration right now:

- planning wrappers that mainly overlap with `/plan`
- default review wrappers that mainly overlap with `/review`
- generic PR wrappers that mainly overlap with `/delegate` or built-in PR flows
- broader BA phase-by-phase orchestration prompts that can likely collapse into
  the smaller retained BA set over time

## Status

This workspace is a proposal and staging area. It is **not yet wired into `deploy-skills`** and does not replace `vscode/`.
