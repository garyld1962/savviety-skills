# Copilot CLI Skills Port & Optimization Plan

**Goal:** Bring Claude skills (`claude/`) into the Copilot CLI canonical structure (`copilot/`) using a built-in-first philosophy. Port functionality, not form — prefer Copilot platform features over command-for-command copies.

**Date:** 2026-05-05  
**Source:** `claude/` — 39 user-invokable skills + 7 internal rubrics  
**Target:** `copilot/` — currently 13 agents, 24 skills, 33 prompts, 3 instructions

**Naming principle:** Claude and Copilot share a skill name vocabulary. A developer switching platforms should be able to invoke the same conceptual command without re-learning names. Claude's names are the canonical source of truth for shared skills.

---

## 0. Naming Parity — Renames Required in `copilot/`

These existing Copilot files must be renamed before or alongside porting. All renames are git mv so history is preserved.

### Prompts to rename

| Current path | Rename to | Claude skill |
|---|---|---|
| `prompts/common/environment-check.prompt.md` | `prompts/common/env-check.prompt.md` | `env-check` |
| `prompts/dev/autonomous-development-kickoff.prompt.md` | `prompts/dev/kickoff.prompt.md` | `kickoff` |
| `prompts/dev/dependency-audit.prompt.md` | `prompts/dev/dep-audit.prompt.md` | `dep-audit` |
| `prompts/dev/migration-guide.prompt.md` | `prompts/dev/dep-migrate.prompt.md` | `dep-migrate` |
| `prompts/dev/investigate-code.prompt.md` | `prompts/dev/code-investigate.prompt.md` | `code-investigate` |
| `prompts/dev/k8s-deploy-verify.prompt.md` | `prompts/dev/k8s-verify.prompt.md` | `k8s-verify` |
| `prompts/dev/ado-item.prompt.md` | `prompts/dev/work-item.prompt.md` | `work-item` |
| `prompts/dev/adversarial-review.prompt.md` | `prompts/review/review-adversarial.prompt.md` | `review-adversarial` (also moves category) |
| `prompts/dev/copilot-asset-audit.prompt.md` | `prompts/dev/skill-audit.prompt.md` | `skill-audit` |
| `prompts/ba/prd-validator.prompt.md` | `prompts/ba/prd-validate.prompt.md` | `prd-validate` |
| `prompts/review/adversarial-review-gauntlet.prompt.md` | `prompts/review/review-gauntlet.prompt.md` | `review-gauntlet` |
| `prompts/review/professional-review.prompt.md` | `prompts/review/code-review-professional.prompt.md` | `code-review-professional` |

### Prompts to evaluate (no Claude equivalent — keep or drop)

| File | Notes |
|---|---|
| `prompts/dev/execute-workflow.prompt.md` | Copilot-specific orchestration; no Claude equivalent. Evaluate: merge into `kickoff` or keep as Copilot-only. |

### Skills to rename

Skills are knowledge assets (auto-discovered, not invoked by name), so naming parity is less critical. Rename only where a developer would need to cross-reference between platforms by name:

| Current path | Rename to | Reason |
|---|---|---|
| `skills/k8s-verification` | `skills/k8s-verify` | Matches Claude `k8s-verify` exactly |
| `skills/adversarial-review` | `skills/review-adversarial` | Matches Claude `review-adversarial` verb-object order |

### Skills to keep as-is (descriptive names preferred over command parity)

| Skill | Claude equivalent | Why keep |
|---|---|---|
| `skills/prd-readiness` | `_internal/aers-readiness` | More descriptive for knowledge consumers |
| `skills/dependency-change-management` | `_internal/dependency-classification` | More descriptive |
| `skills/execution-environment` | `env-check` | Knowledge rubric, not a command |
| `skills/review-engine` | `code-review` | Implementation name; `code-review.prompt.md` is the user-facing name |
| `skills/ado-work-items` | `work-item` | Implementation-level connector; prompt name changed |
| `skills/code-investigation-orchestrator` | internal | Implementation detail |
| `skills/code-investigation-search` | internal | Implementation detail |

### BA prompts — no rename needed

The BA prompt set (`ba-context-builder`, `ba-eval-harness`, `ba-knowledge-capture`, `ba-problem-refiner`, `ba-spec-engineer`) has no Claude equivalent and uses its own naming convention. Leave as-is.

### Review domain prompts — no rename needed

`review-api`, `review-db`, `review-design`, `review-tests` have no Claude equivalents. Leave as-is.

---

## 1. Canonical Copilot CLI Structure (2025–2026)

As of GA (February 2026) and Skills GA (December 2025):

```
copilot/
├── copilot-instructions.md          # Repo-wide passive instructions (no frontmatter)
├── instructions/
│   └── *.instructions.md            # Path-scoped rules (applyTo: glob frontmatter)
├── prompts/
│   ├── ba/                          # User-invokable slash-command workflows
│   ├── dev/
│   ├── review/
│   └── common/
├── agents/
│   └── *.agent.md                   # Specialist persona agents
├── skills/
│   └── {skill-name}/
│       ├── SKILL.md                 # Required: name + description frontmatter
│       └── references/              # Optional: rubrics, overlays, sub-content
└── templates/
```

**Key format differences from Claude:**

| Claude | Copilot |
|--------|---------|
| `name:` + `description:` frontmatter | `name:` + `description:` — same, but `description` is the auto-discovery trigger (must be rich) |
| `model: opus/haiku` | Not supported in skill frontmatter; omit |
| `user-invocable: false` / `private-resource: true` | No equivalent; embed content or put in `references/` |
| `Agent tool` dispatch | Use `/fleet` built-in or `agents/*.agent.md` |
| `TaskCreate/TaskUpdate` | No equivalent; remove |
| `CLAUDE.md` | `copilot-instructions.md` |
| `~/.claude/env.config.md` | `copilot/templates/env.config.template.md` |
| `Read`, `Write`, `Edit`, `Grep`, `Glob` | `read`, `edit`, `search`, `codebase`, `shell` |
| `superpowers:*` skill references | Describe the behavior inline |

---

## 2. Guiding Strategy

From `copilot/platform-review.md` — the platform-native philosophy:

- **Built-ins first.** `/plan`, `/review`, `/research`, `/fleet`, `/tasks`, `/diff`, `/pr` cover large categories. Don't wrap them.
- **Custom prompts for high-value gaps only.** A prompt that just calls `/plan` with a header is not a prompt.
- **Skills hold durable knowledge** — rubrics, checklists, heuristics, domain rules.
- **Instructions hold passive invariants** — always-on rules that apply without invocation.
- **Agents stay narrow** — bounded specialist roles, not generic orchestrators.

---

## 3. Gap Analysis — Claude vs Current Copilot

### Already Covered (review and update only)

| Claude Skill | Copilot Asset | Status |
|---|---|---|
| `checkpoint` | `prompts/dev/checkpoint.prompt.md` | Update with Claude skill's tooling-detection logic |
| `code-review` | `prompts/review/code-review.prompt.md` + `skills/review-engine/` | Already stronger in Copilot; verify parity |
| `code-review-professional` | `prompts/review/professional-review.prompt.md` | Add rubric from `_internal/professional-rubric` as skill |
| `code-investigate` | `prompts/dev/investigate-code.prompt.md` + investigation agents | Verify structured report contract matches Claude |
| `configure` | `prompts/common/configure.prompt.md` | Add pre-flight-check pattern from `_internal/pre-flight-check` |
| `dep-audit` | `prompts/dev/dependency-audit.prompt.md` | Enrich with dep-classification taxonomy from `_internal/dependency-classification` |
| `dep-migrate` | `prompts/dev/migration-guide.prompt.md` | Add breaking-change mapping workflow from Claude skill |
| `env-check` | `prompts/common/environment-check.prompt.md` + `skills/execution-environment/` | Review for parity |
| `execute-plan` | `prompts/dev/execute-plan.prompt.md` | Major update — Claude skill is far more detailed (see §4) |
| `hotfix` | `prompts/dev/hotfix.prompt.md` | Update with security-quick-check step |
| `ideate` | `prompts/ba/ideate.prompt.md` | Add tech mode from Claude skill; BA mode already present |
| `k8s-verify` | `prompts/dev/k8s-deploy-verify.prompt.md` | Update with Claude skill's endpoint and event checks |
| `kickoff` | `prompts/dev/autonomous-development-kickoff.prompt.md` | Major update — Claude skill has readiness gate |
| `postmortem` | `prompts/dev/postmortem.prompt.md` | Update with taxonomy-tagged recommendation output |
| `prd-validate` | `prompts/ba/prd-validator.prompt.md` + `skills/prd-readiness/` | Update interview flow from Claude skill |
| `review-adversarial` | `prompts/dev/adversarial-review.prompt.md` + `agents/adversarial-reviewer.agent.md` | Review for parity; Claude uses Codex/Gemini dispatch |
| `review-gauntlet` | `prompts/review/adversarial-review-gauntlet.prompt.md` | Update 3-lens pattern from Claude skill |
| `ship` | `prompts/dev/ship.prompt.md` | Add CLAUDE.md → copilot-instructions.md config lookup |
| `skill-audit` | `prompts/dev/copilot-asset-audit.prompt.md` | Enrich with Claude's gap-analysis + marketplace steps |
| `skill-help` | `prompts/dev/skill-help.prompt.md` | Update to reference `/skills` built-in and awesome-copilot |
| `test-plan` | `prompts/dev/test-plan.prompt.md` + `skills/test-planning/` | Add 4 analyst sub-skills as references; enrich test-writer |
| `ubiquitous-language` | `prompts/ba/ubiquitous-language.prompt.md` | Review for parity |
| `work-item` | `prompts/dev/ado-item.prompt.md` | **Rename to `work-item.prompt.md`**; add Linear support alongside ADO |
| `_internal/disposition` | `skills/review-disposition-governance/SKILL.md` | Already present; verify vocabulary matches Claude |
| `_internal/repo-delivery` | `skills/repo-delivery/SKILL.md` | Already present; verify schema matches Claude |
| `_internal/aers-readiness` | `skills/prd-readiness/SKILL.md` | Already present; verify sections match Claude rubric |

### Missing — New Copilot Assets Needed

| Claude Skill | Recommended Copilot Target | Priority |
|---|---|---|
| `execute-prd` | `prompts/dev/execute-prd.prompt.md` | P1 — key orchestrator |
| `prd-acceptance` | `prompts/dev/prd-acceptance.prompt.md` | P1 — post-implementation gate |
| `spec-review-adversarial` | `prompts/review/spec-review-adversarial.prompt.md` | P1 — BA validation |
| `triage` | `prompts/dev/triage.prompt.md` | P1 — bug investigation |
| `thesis` | `prompts/dev/thesis.prompt.md` | P2 — product/arch thesis |
| `grill-me` | `prompts/dev/grill-me.prompt.md` | P2 — decision stress-test |
| `process-tune` | `prompts/dev/process-tune.prompt.md` | P2 — postmortem feedback loop |
| `changelog` | `prompts/dev/changelog.prompt.md` | P2 — release workflow |
| `sync-main` | `prompts/dev/sync-main.prompt.md` | P3 — rely on `/pr` first; add only for rebase conflict logic |
| `repo-status` | `prompts/dev/repo-status.prompt.md` | P3 — `/diff` + `/pr` cover most; add for session-orient snapshot |
| `what-is-it-about` | `prompts/dev/video-thesis.prompt.md` | P3 — domain-specific, low priority |
| `parallel-optimization` | `skills/parallel-optimization/SKILL.md` | P2 — embed as skill used by execute-plan/execute-prd |
| `_internal/professional-rubric` | `skills/professional-review-rubric/SKILL.md` | P1 — already referenced by professional-review prompt |
| `_internal/dependency-classification` | Add to `skills/dependency-change-management/SKILL.md` | P2 — enrich existing skill |
| `_internal/security-quick-check` | Add as `skills/review-engine/concept/security-quick.md` | P2 — supplement existing security concept |
| `_internal/pre-flight-check` | `skills/pre-flight-pattern/SKILL.md` | P3 — referenced by configure and kickoff |
| `pr` (full lifecycle) | Decompose: keep `/pr` built-in for inspection; add `prompts/dev/pr-create.prompt.md` for the governed commit+push+PR-create flow | P2 |
| `validate-plan` | Embed check into `execute-plan.prompt.md` preamble | P2 — no need for standalone |
| `audit-existing` | `prompts/dev/audit-existing.prompt.md` | P2 — pre-planning repo audit |

### Covered by Copilot Built-ins (do not port)

| Claude Skill | Replaced By |
|---|---|
| `find-skills` | `/skills` built-in + Copilot marketplace UI |
| `validate-plan` (standalone) | Embed in `execute-plan`; `/plan` covers lighter cases |
| `sync-main` (basic) | Copilot understands git state; mention `/diff` in context |
| `repo-status` (basic) | `/diff` + `/pr` + `/context` cover most use cases |
| `review-adversarial` model-switch | `/model` built-in handles second-opinion passes |

---

## 4. Major Skills Requiring Significant Rework

### `execute-plan` → `prompts/dev/execute-plan.prompt.md`

Claude's `execute-plan` is the most complex skill (76KB). The Copilot prompt exists but is a thin wrapper. Needed additions:

- Phase 0: `validate-plan` gate (port as inline pre-flight check)
- Phase 1: interactive ambiguity handling (`--interactive` arg)
- Phase 1.5: parallel-agent lane map (reference `skills/parallel-optimization/`)
- Phase 2: per-task TDD cycle (reference `skills/test-planning/`)
- Phase 3: `diff_manifest` for scoped review dispatch
- Phase 4: milestone breakpoints with `skills/review-engine/` dispatch
- Phase 5: PR boundary — full review + professional grade
- Phase 6: postmortem auto-fire
- Decision-record governance (reference `skills/review-disposition-governance/`)
- **Replace:** `TaskCreate/TaskUpdate` → `/tasks` built-in or remove
- **Replace:** `Agent tool` dispatch → `/fleet` with specialist agents

### `kickoff` → `prompts/dev/autonomous-development-kickoff.prompt.md`

Current Copilot version lacks the readiness gate. Add:
- AERS readiness check (reference `skills/prd-readiness/`)
- Built-in first: call `/plan` then hand to `execute-plan`
- Remove `superpowers:*` references; describe behavior inline
- Remove Claude's `model: opus` override

### `code-review-professional` + `_internal/professional-rubric`

The rubric is not yet a standalone Copilot skill. Create:
- `skills/professional-review-rubric/SKILL.md` — 7 axes, seniority grades
- Update `prompts/review/professional-review.prompt.md` to reference the skill

### `work-item` → rename + extend `prompts/dev/ado-item.prompt.md`

Current Copilot version is ADO-only. Claude version is also ADO-only. The Claude MCP linear tools are available — extend to support Linear via MCP.

---

## 5. Internal Skill Disposition

| Claude Internal Skill | Copilot Action |
|---|---|
| `_internal/aers-readiness` | Already exists as `skills/prd-readiness/SKILL.md`. Verify completeness. |
| `_internal/dependency-classification` | Merge taxonomy into `skills/dependency-change-management/SKILL.md` |
| `_internal/disposition` | Already exists as `skills/review-disposition-governance/SKILL.md`. Verify vocabulary. |
| `_internal/pre-flight-check` | Create `skills/pre-flight-pattern/SKILL.md` for configure + kickoff to reference |
| `_internal/professional-rubric` | Create `skills/professional-review-rubric/SKILL.md` |
| `_internal/repo-delivery` | Already exists as `skills/repo-delivery/SKILL.md`. Verify schema. |
| `_internal/security-quick-check` | Append to `skills/review-engine/concept/security.md` as a `## Quick Pass` section |

### Test-plan sub-skills

The 4 analysts (`contract-compliance`, `boundary-validation`, `integration-surface`, `state-lifecycle`) and `test-writer` are private sub-skills.

- Add to `skills/test-planning/references/` as individual Markdown files
- Reference them from `skills/test-planning/SKILL.md` body
- Do not expose as standalone Copilot skills (no `SKILL.md` per analyst)

---

## 6. Execution Order (by dependency)

### Phase 0 — Renames (do first, before any content changes)

All renames use `git mv` to preserve history. Group into one commit.

```bash
cd copilot/prompts
git mv common/environment-check.prompt.md common/env-check.prompt.md
git mv dev/autonomous-development-kickoff.prompt.md dev/kickoff.prompt.md
git mv dev/dependency-audit.prompt.md dev/dep-audit.prompt.md
git mv dev/migration-guide.prompt.md dev/dep-migrate.prompt.md
git mv dev/investigate-code.prompt.md dev/code-investigate.prompt.md
git mv dev/k8s-deploy-verify.prompt.md dev/k8s-verify.prompt.md
git mv dev/ado-item.prompt.md dev/work-item.prompt.md
git mv dev/adversarial-review.prompt.md review/review-adversarial.prompt.md
git mv dev/copilot-asset-audit.prompt.md dev/skill-audit.prompt.md
git mv ba/prd-validator.prompt.md ba/prd-validate.prompt.md
git mv review/adversarial-review-gauntlet.prompt.md review/review-gauntlet.prompt.md
git mv review/professional-review.prompt.md review/code-review-professional.prompt.md

cd ../skills
git mv k8s-verification k8s-verify
git mv adversarial-review review-adversarial
```

After renaming, update any cross-references inside files that mention the old names.

### Phase 1 — Foundation (unblock everything else)
Verify and patch existing skills that prompts depend on:

1. Verify `skills/prd-readiness/SKILL.md` matches `_internal/aers-readiness`
2. Verify `skills/review-disposition-governance/SKILL.md` matches `_internal/disposition`
3. Verify `skills/repo-delivery/SKILL.md` matches `_internal/repo-delivery`
4. Create `skills/professional-review-rubric/SKILL.md` from `_internal/professional-rubric`
5. Enrich `skills/dependency-change-management/SKILL.md` with `_internal/dependency-classification` taxonomy
6. Append quick-check section to `skills/review-engine/concept/security.md` from `_internal/security-quick-check`
7. Create `skills/parallel-optimization/SKILL.md` from `claude/parallel-optimization`
8. Add test-plan analyst references to `skills/test-planning/references/`

### Phase 2 — Missing P1 Prompts (high-value gaps)
New prompts for functionality not yet in Copilot:

9. `prompts/dev/execute-prd.prompt.md` — from `claude/execute-prd`
10. `prompts/dev/prd-acceptance.prompt.md` — from `claude/prd-acceptance`
11. `prompts/review/spec-review-adversarial.prompt.md` — from `claude/spec-review-adversarial`
12. `prompts/dev/triage.prompt.md` — from `claude/triage`

### Phase 3 — Major Prompt Updates
Existing prompts that need significant content from Claude skills:

13. `prompts/dev/execute-plan.prompt.md` — major update (see §4)
14. `prompts/dev/autonomous-development-kickoff.prompt.md` — add readiness gate
15. `prompts/review/professional-review.prompt.md` — wire up professional-review-rubric skill
16. `prompts/dev/work-item.prompt.md` — rename from ado-item; add Linear support

### Phase 4 — Missing P2 Prompts
17. `prompts/dev/audit-existing.prompt.md` — from `claude/audit-existing`
18. `prompts/dev/pr-create.prompt.md` — governed PR flow (not inspect — that's `/pr` built-in)
19. `prompts/dev/changelog.prompt.md` — from `claude/changelog`
20. `prompts/dev/thesis.prompt.md` — from `claude/thesis`
21. `prompts/dev/grill-me.prompt.md` — from `claude/grill-me`
22. `prompts/dev/process-tune.prompt.md` — from `claude/process-tune`
23. Embed validate-plan check into `execute-plan.prompt.md` preamble

### Phase 5 — Minor Updates and P3 Prompts
24. `prompts/dev/checkpoint.prompt.md` — add tooling-detection from Claude skill
25. `prompts/dev/hotfix.prompt.md` — add security-quick-check reference
26. `prompts/dev/skill-help.prompt.md` — update for `/skills` built-in + awesome-copilot
27. `prompts/dev/copilot-asset-audit.prompt.md` — enrich with Claude gap-analysis workflow
28. `prompts/ba/ideate.prompt.md` — add tech mode from Claude skill
29. `prompts/dev/video-thesis.prompt.md` — from `claude/what-is-it-about` (P3)
30. `prompts/dev/repo-status.prompt.md` — from `claude/repo-status` (P3)
31. `prompts/dev/sync-main.prompt.md` — from `claude/sync-main`, rebase conflict focus only (P3)

---

## 7. Cross-Cutting Conventions for All Ports

### Frontmatter
```yaml
---
description: >
  [Rich one-paragraph trigger description — this is how Copilot auto-discovers the skill.
  Include synonyms, example phrases a user might say, and adjacent use cases.]
argument-hint: "<name-or-path> [--flag value]"      # if the prompt takes arguments
agent: agent                                          # omit for simple ask prompts
tools:                                               # only when restricting tools
  - shell
  - read
  - edit
---
```

- Remove `name:` if redundant with filename (Copilot defaults to filename)
- Remove `model:` — not a supported frontmatter field in skills or prompts
- Remove `user-invocable:`, `private-resource:`, `internal:` — not Copilot fields

### Description Enrichment
Claude descriptions are terse (`"Audit a repository before planning"`). Copilot descriptions drive auto-discovery — expand each to include:
- What it does (1 sentence)
- When to use it (trigger phrases)
- What it produces
- What NOT to use it for (critical: prevents misfire)

### Tool Reference Replacements
| Claude | Copilot |
|--------|---------|
| `CLAUDE.md` | `copilot-instructions.md` |
| `~/.claude/env.config.md` | `templates/env.config.template.md` |
| `Agent tool` with `subagent_type=Explore` | `/research` built-in |
| `Agent tool` with parallel workers | `/fleet` + agents |
| `TaskCreate/TaskUpdate` | `/tasks` built-in or remove |
| `superpowers:brainstorming` | Describe the divergent-thinking step inline |
| `superpowers:writing-plans` | Describe the plan-writing step inline |
| `superpowers:test-driven-development` | Reference `skills/test-planning/` |
| `superpowers:systematic-debugging` | Describe the debug loop inline |
| `Skill tool` | No equivalent; inline the referenced skill content or use `#file:` mention |

### Built-in Preference Notes (add to relevant prompts)
Where a Claude skill wraps a built-in behavior, note it:
```
> **Note:** This prompt extends `/review`. For a quick review without the full
> domain-dispatch framework, prefer `/review` directly.
```

---

## 8. Files to Commit After Port

Deliverables at completion:

**Renamed (Phase 0 — git mv):**
- `prompts/common/env-check.prompt.md` (was `environment-check`)
- `prompts/dev/kickoff.prompt.md` (was `autonomous-development-kickoff`)
- `prompts/dev/dep-audit.prompt.md` (was `dependency-audit`)
- `prompts/dev/dep-migrate.prompt.md` (was `migration-guide`)
- `prompts/dev/code-investigate.prompt.md` (was `investigate-code`)
- `prompts/dev/k8s-verify.prompt.md` (was `k8s-deploy-verify`)
- `prompts/dev/work-item.prompt.md` (was `ado-item`)
- `prompts/review/review-adversarial.prompt.md` (was `dev/adversarial-review`)
- `prompts/dev/skill-audit.prompt.md` (was `copilot-asset-audit`)
- `prompts/ba/prd-validate.prompt.md` (was `prd-validator`)
- `prompts/review/review-gauntlet.prompt.md` (was `adversarial-review-gauntlet`)
- `prompts/review/code-review-professional.prompt.md` (was `professional-review`)
- `skills/k8s-verify/` (was `k8s-verification`)
- `skills/review-adversarial/` (was `adversarial-review`)

**New files:**
- `copilot/skills/professional-review-rubric/SKILL.md`
- `copilot/skills/parallel-optimization/SKILL.md`
- `copilot/skills/pre-flight-pattern/SKILL.md`
- `copilot/skills/test-planning/references/{5 analyst files}`
- `copilot/prompts/dev/execute-prd.prompt.md`
- `copilot/prompts/dev/prd-acceptance.prompt.md`
- `copilot/prompts/review/spec-review-adversarial.prompt.md`
- `copilot/prompts/dev/triage.prompt.md`
- `copilot/prompts/dev/audit-existing.prompt.md`
- `copilot/prompts/dev/pr.prompt.md`
- `copilot/prompts/dev/changelog.prompt.md`
- `copilot/prompts/dev/thesis.prompt.md`
- `copilot/prompts/dev/grill-me.prompt.md`
- `copilot/prompts/dev/process-tune.prompt.md`
- `copilot/prompts/dev/what-is-it-about.prompt.md` (P3)
- `copilot/prompts/dev/repo-status.prompt.md` (P3)
- `copilot/prompts/dev/sync-main.prompt.md` (P3)

**Updated files (major):**
- `copilot/prompts/dev/execute-plan.prompt.md`
- `copilot/prompts/dev/kickoff.prompt.md` (renamed + major update)
- `copilot/prompts/review/code-review-professional.prompt.md` (renamed + skill wiring)
- `copilot/prompts/dev/work-item.prompt.md` (renamed + Linear support)
- `copilot/skills/dependency-change-management/SKILL.md`
- `copilot/skills/review-engine/concept/security.md`
- `copilot/skills/test-planning/SKILL.md`

**Verify (read + confirm parity, update if needed):**
- `copilot/skills/prd-readiness/SKILL.md`
- `copilot/skills/review-disposition-governance/SKILL.md`
- `copilot/skills/repo-delivery/SKILL.md`

**Asset catalog:**
- Update `copilot/asset-catalog.md` after each phase

---

## 9. Out of Scope (deliberate)

| Claude Skill | Reason Not Ported |
|---|---|
| `find-skills` | `/skills` built-in replaces; awesome-copilot marketplace is the native path |
| `skill-audit` (Claude-specific parts) | Port only Copilot-aware asset audit; drop Claude registry scanning |
| All `superpowers:*` sub-skills | Claude Code SDK constructs; no Copilot equivalent; describe inline in consuming prompts |
| CCX event log integration | Claude Code-specific persistence layer |
| RTK proxy references | Claude Code hook system; no Copilot equivalent |
| `.claude/settings.json` hook patterns | Copilot CLI uses `hooks.json`; separate project if needed |
