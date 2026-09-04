# Claude → Codex / GitHub Copilot coverage

All 48 public Claude workflows have an explicit native entrypoint or intentional
consolidation. This records coverage, not equivalence of runtime internals. Codex
uses 44 skill entrypoints. Copilot durable skills work across skill-capable hosts;
prompt-only mappings require a prompt-capable host. Prompt shortcuts are optional
for the newly added capabilities and core planning/execution workflows.

The source of the mapping is claude-native.json. Native execution uses the shared
task graph and proof contract; it does not run the Claude Workflow scripts.

| Claude workflow | Codex entrypoint | Copilot entrypoint |
|---|---|---|
| audit-existing | [audit-existing](../../codex/plugins/savviety-workflows/skills/audit-existing/SKILL.md) | [prompt](../../copilot/prompts/dev/audit-existing.prompt.md) |
| bug-session | [bug-session](../../codex/plugins/savviety-workflows/skills/bug-session/SKILL.md) | [skill](../../copilot/skills/bug-session/SKILL.md), [prompt](../../copilot/prompts/dev/bug-session.prompt.md) |
| changelog | [changelog](../../codex/plugins/savviety-workflows/skills/changelog/SKILL.md) | [prompt](../../copilot/prompts/dev/changelog.prompt.md) |
| checkpoint | [checkpoint](../../codex/plugins/savviety-workflows/skills/checkpoint/SKILL.md) | [prompt](../../copilot/prompts/dev/checkpoint.prompt.md) |
| code-investigate | [code-investigate](../../codex/plugins/savviety-workflows/skills/code-investigate/SKILL.md) | [prompt](../../copilot/prompts/dev/code-investigate.prompt.md) |
| code-review-professional | [code-review-professional](../../codex/plugins/savviety-workflows/skills/code-review-professional/SKILL.md) | [prompt](../../copilot/prompts/review/code-review-professional.prompt.md) |
| configure | [configure](../../codex/plugins/savviety-workflows/skills/configure/SKILL.md) | [skill](../../copilot/skills/configure/SKILL.md), [prompt](../../copilot/prompts/common/configure.prompt.md) |
| dep-audit | [dep-audit](../../codex/plugins/savviety-workflows/skills/dep-audit/SKILL.md) | [prompt](../../copilot/prompts/dev/dep-audit.prompt.md) |
| dep-migrate | [dep-migrate](../../codex/plugins/savviety-workflows/skills/dep-migrate/SKILL.md) | [prompt](../../copilot/prompts/dev/dep-migrate.prompt.md) |
| design-twice | [design-twice](../../codex/plugins/savviety-workflows/skills/design-twice/SKILL.md) | [skill](../../copilot/skills/design-twice/SKILL.md), [prompt](../../copilot/prompts/ba/design-twice.prompt.md) |
| domain-review | [code-review](../../codex/plugins/savviety-workflows/skills/code-review/SKILL.md) | [prompt](../../copilot/prompts/review/domain-review.prompt.md) |
| drawio | [drawio](../../codex/plugins/savviety-workflows/skills/drawio/SKILL.md) | [skill](../../copilot/skills/drawio/SKILL.md), [prompt](../../copilot/prompts/common/drawio.prompt.md) |
| env-check | [env-check](../../codex/plugins/savviety-workflows/skills/env-check/SKILL.md) | [prompt](../../copilot/prompts/common/env-check.prompt.md) |
| execute-plan | [execute-plan](../../codex/plugins/savviety-workflows/skills/execute-plan/SKILL.md) | [skill](../../copilot/skills/execute-plan/SKILL.md), [prompt](../../copilot/prompts/dev/execute-plan.prompt.md) |
| execute-prd | [execute-prd](../../codex/plugins/savviety-workflows/skills/execute-prd/SKILL.md) | [skill](../../copilot/skills/execute-prd/SKILL.md), [prompt](../../copilot/prompts/dev/execute-prd.prompt.md) |
| feature-sweep | [feature-sweep](../../codex/plugins/savviety-workflows/skills/feature-sweep/SKILL.md) | [skill](../../copilot/skills/feature-sweep/SKILL.md), [prompt](../../copilot/prompts/common/feature-sweep.prompt.md) |
| gh-readiness | [gh-readiness](../../codex/plugins/savviety-workflows/skills/gh-readiness/SKILL.md) | [skill](../../copilot/skills/gh-readiness/SKILL.md), [prompt](../../copilot/prompts/common/gh-readiness.prompt.md) |
| goal | [goal](../../codex/plugins/savviety-workflows/skills/goal/SKILL.md) | [skill](../../copilot/skills/goal/SKILL.md), [prompt](../../copilot/prompts/ba/goal.prompt.md) |
| grill-me | [grill-me](../../codex/plugins/savviety-workflows/skills/grill-me/SKILL.md) | [prompt](../../copilot/prompts/dev/grill-me.prompt.md) |
| hotfix | [ship](../../codex/plugins/savviety-workflows/skills/ship/SKILL.md) | [prompt](../../copilot/prompts/dev/hotfix.prompt.md) |
| ideate | [ideate](../../codex/plugins/savviety-workflows/skills/ideate/SKILL.md) | [prompt](../../copilot/prompts/ba/ideate.prompt.md) |
| issue-slices | [issue-slices](../../codex/plugins/savviety-workflows/skills/issue-slices/SKILL.md) | [skill](../../copilot/skills/issue-slices/SKILL.md), [prompt](../../copilot/prompts/ba/issue-slices.prompt.md) |
| k8s-verify | [k8s-verify](../../codex/plugins/savviety-workflows/skills/k8s-verify/SKILL.md) | [skill](../../copilot/skills/k8s-verify/SKILL.md), [prompt](../../copilot/prompts/dev/k8s-verify.prompt.md) |
| kickoff | [execute-prd](../../codex/plugins/savviety-workflows/skills/execute-prd/SKILL.md) | [prompt](../../copilot/prompts/dev/kickoff.prompt.md) |
| modernize | [modernize](../../codex/plugins/savviety-workflows/skills/modernize/SKILL.md) | [prompt](../../copilot/prompts/dev/modernize.prompt.md) |
| parallel-optimization | [parallel-optimization](../../codex/plugins/savviety-workflows/skills/parallel-optimization/SKILL.md) | [skill](../../copilot/skills/parallel-optimization/SKILL.md), [prompt](../../copilot/prompts/dev/parallel-optimization.prompt.md) |
| postmortem | [postmortem](../../codex/plugins/savviety-workflows/skills/postmortem/SKILL.md) | [prompt](../../copilot/prompts/dev/postmortem.prompt.md) |
| pr | [ship](../../codex/plugins/savviety-workflows/skills/ship/SKILL.md) | [prompt](../../copilot/prompts/dev/pr.prompt.md) |
| prd-acceptance | [prd-acceptance](../../codex/plugins/savviety-workflows/skills/prd-acceptance/SKILL.md) | [skill](../../copilot/skills/prd-acceptance/SKILL.md), [prompt](../../copilot/prompts/dev/prd-acceptance.prompt.md) |
| prd-validate | [prd-validate](../../codex/plugins/savviety-workflows/skills/prd-validate/SKILL.md) | [prompt](../../copilot/prompts/ba/prd-validate.prompt.md) |
| process-tune | [process-tune](../../codex/plugins/savviety-workflows/skills/process-tune/SKILL.md) | [prompt](../../copilot/prompts/dev/process-tune.prompt.md) |
| refactor-brief | [refactor-brief](../../codex/plugins/savviety-workflows/skills/refactor-brief/SKILL.md) | [skill](../../copilot/skills/refactor-brief/SKILL.md), [prompt](../../copilot/prompts/dev/refactor-brief.prompt.md) |
| repo-status | [repo-status](../../codex/plugins/savviety-workflows/skills/repo-status/SKILL.md) | [prompt](../../copilot/prompts/dev/repo-status.prompt.md) |
| review-adversarial | [review-adversarial](../../codex/plugins/savviety-workflows/skills/review-adversarial/SKILL.md) | [skill](../../copilot/skills/review-adversarial/SKILL.md), [prompt](../../copilot/prompts/review/review-adversarial.prompt.md) |
| review-gauntlet | [review-gauntlet](../../codex/plugins/savviety-workflows/skills/review-gauntlet/SKILL.md) | [prompt](../../copilot/prompts/review/review-gauntlet.prompt.md) |
| ship | [ship](../../codex/plugins/savviety-workflows/skills/ship/SKILL.md) | [prompt](../../copilot/prompts/dev/ship.prompt.md) |
| skill-audit | [skills](../../codex/plugins/savviety-workflows/skills/skills/SKILL.md) | [prompt](../../copilot/prompts/dev/skill-audit.prompt.md) |
| skill-help | [skills](../../codex/plugins/savviety-workflows/skills/skills/SKILL.md) | [prompt](../../copilot/prompts/dev/skill-help.prompt.md) |
| spec-review-adversarial | [spec-review-adversarial](../../codex/plugins/savviety-workflows/skills/spec-review-adversarial/SKILL.md) | [prompt](../../copilot/prompts/review/spec-review-adversarial.prompt.md) |
| sync-main | [sync-main](../../codex/plugins/savviety-workflows/skills/sync-main/SKILL.md) | [prompt](../../copilot/prompts/dev/sync-main.prompt.md) |
| test-plan | [test-plan](../../codex/plugins/savviety-workflows/skills/test-plan/SKILL.md) | [prompt](../../copilot/prompts/dev/test-plan.prompt.md) |
| thesis | [thesis](../../codex/plugins/savviety-workflows/skills/thesis/SKILL.md) | [prompt](../../copilot/prompts/dev/thesis.prompt.md) |
| triage | [triage](../../codex/plugins/savviety-workflows/skills/triage/SKILL.md) | [prompt](../../copilot/prompts/dev/triage.prompt.md) |
| ubiquitous-language | [ubiquitous-language](../../codex/plugins/savviety-workflows/skills/ubiquitous-language/SKILL.md) | [prompt](../../copilot/prompts/ba/ubiquitous-language.prompt.md) |
| validate-plan | [validate-plan](../../codex/plugins/savviety-workflows/skills/validate-plan/SKILL.md) | [skill](../../copilot/skills/validate-plan/SKILL.md), [prompt](../../copilot/prompts/dev/validate-plan.prompt.md) |
| vault | [vault](../../codex/plugins/savviety-workflows/skills/vault/SKILL.md) | [skill](../../copilot/skills/vault/SKILL.md), [prompt](../../copilot/prompts/common/vault.prompt.md) |
| what-is-it-about | [what-is-it-about](../../codex/plugins/savviety-workflows/skills/what-is-it-about/SKILL.md) | [prompt](../../copilot/prompts/dev/what-is-it-about.prompt.md) |
| work-item | [work-item](../../codex/plugins/savviety-workflows/skills/work-item/SKILL.md) | [prompt](../../copilot/prompts/dev/work-item.prompt.md) |
