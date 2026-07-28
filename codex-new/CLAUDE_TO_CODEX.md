# Claude To Codex Skill Map

This tree recreates the Claude skills as the `codex-skills` Codex plugin plus Codex-native agents, hooks, rules, scripts, and references.

## Direct Skills

| Claude skill | Codex skill |
| --- | --- |
| `audit-existing` | `audit-existing` |
| `changelog` | `changelog` |
| `checkpoint` | `checkpoint` |
| `code-investigate` | `code-investigate` |
| `code-review-professional` | `code-review-professional` |
| `configure` | `configure` |
| `dep-audit` | `dep-audit` |
| `dep-migrate` | `dep-migrate` |
| `drawio` | `drawio` |
| `env-check` | `env-check` |
| `execute-plan` | `execute-plan` |
| `execute-prd` | `execute-prd` |
| `grill-me` | `grill-me` |
| `ideate` | `ideate` |
| `k8s-verify` | `k8s-verify` |
| `modernize` | `modernize` |
| `parallel-optimization` | `parallel-optimization` |
| `postmortem` | `postmortem` |
| `prd-acceptance` | `prd-acceptance` |
| `prd-validate` | `prd-validate` |
| `process-tune` | `process-tune` |
| `repo-status` | `repo-status` |
| `review-adversarial` | `review-adversarial` |
| `review-gauntlet` | `review-gauntlet` |
| `ship` | `ship` |
| `spec-review-adversarial` | `spec-review-adversarial` |
| `sync-main` | `sync-main` |
| `test-plan` | `test-plan` |
| `thesis` | `thesis` |
| `triage` | `triage` |
| `ubiquitous-language` | `ubiquitous-language` |
| `validate-plan` | `validate-plan` |
| `what-is-it-about` | `what-is-it-about` |
| `work-item` | `work-item` |

## Codex Consolidations

| Claude source | Codex treatment |
| --- | --- |
| `domain-review` | Recreated as `code-review`, using Codex review stance and reference-loaded concept/platform lenses. |
| `hotfix`, `pr`, `ship` | Recreated as one `ship` workflow with default, release, and fast modes. Remote mutation still requires explicit approval. |
| `kickoff`, `execute-prd` | Recreated as `execute-prd`; it handles PRD/story intake, plan generation, and execution handoff. |
| `skill-audit`, `skill-help` | Recreated as `skills`, including listing, detail, audit, native-overlap, and discovery modes. |
| `test-plan/analysts/*`, `test-plan/test-writer` | Recreated as `test-plan` references instead of user-triggered subskills. |
| `_internal/*` | Recreated as per-skill `references/` so Codex loads only the relevant rubric or contract. |

## Native Codex Features Used

- `.codex-plugin/plugin.json` packages the skills as an installable local plugin.
- `agents/openai.yaml` gives each skill UI metadata and a default `$skill` prompt.
- `.toml` custom agents model reusable worker roles for plan execution and review.
- `templates/rules/*.rules` models command approval policy instead of prose-only guardrails.
- `templates/hooks/*.py` and plugin `hooks/hooks.json` recreate Claude hook behavior for install scanning, PR guardrails, and session journaling.
- Skill scripts handle deterministic checks and transforms where prose would be fragile.
