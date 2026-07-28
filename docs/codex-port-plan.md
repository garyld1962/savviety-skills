# Codex Port Plan

Status: draft plan  
Reviewed: 2026-05-05  
Scope: optimize the current `claude/` skill set and port it to Codex's current skill, agent, plugin, hook, and prompt-adjacent structure.

## Implementation Progress

Started on 2026-05-05:

- Phase 1 scaffold created under `codex/`.
- Local repo marketplace created at `.claude-plugin/marketplace.json` because `.agents/` is read-only in this workspace.
- `savviety-workflows` plugin manifest created with default starter prompts.
- Six project-scoped custom agents created under `codex/agents/`.
- Codex templates created for `AGENTS.md`, `config.toml`, `hooks.json`, hook scripts, and rules.
- Thirty-three Codex skill surfaces ported into `codex/plugins/savviety-workflows/skills/`; this includes consolidated `ship`, `execute-prd`, and `skills` wrappers plus legacy references for large workflows.
- Structural validator added at `codex/scripts/validate_codex_assets.py`.
- `manifest.json` and `cli/skill.sh` extended with `--codex` install/update support.

## Sources Reviewed

Local source:

- `claude/README.md`
- all `claude/**/SKILL.md` files
- `claude/code-review/**`
- `claude/test-plan/**`
- `claude/execute-plan/agents/*.md`
- `claude/infra/**`
- `manifest.json`
- `docs/consolidation-plan.md`
- `docs/repo-skills-design.md`

Current OpenAI Codex docs:

- Agent Skills: https://developers.openai.com/codex/skills
- Subagents: https://developers.openai.com/codex/subagents
- AGENTS.md: https://developers.openai.com/codex/guides/agents-md
- Build plugins: https://developers.openai.com/codex/plugins/build
- Hooks: https://developers.openai.com/codex/hooks
- Rules: https://developers.openai.com/codex/rules
- Prompting Codex: https://developers.openai.com/codex/prompting

## Current Claude Inventory

The Claude tree contains 48 `SKILL.md` files:

- 36 top-level user-facing skills.
- 7 `_internal` hidden contracts or rubrics.
- 5 `test-plan` private analyst/writer subskills.

Large or structurally important skills:

- `execute-plan` is the largest file by far at 1,864 lines and includes private role prompts in `execute-plan/agents/`.
- `code-review` is a composite controller with `concept/`, `dialect/`, `platform/`, `profiles/`, and `references/`.
- `test-plan` is a composite workflow with private analysts, schemas, rubrics, and writer instructions.
- `review-adversarial`, `spec-review-adversarial`, `execute-prd`, and `parallel-optimization` contain explicit multi-agent or parallel-lane behavior.
- `infra/` contains Claude hook scripts, not skills.

The existing `docs/consolidation-plan.md` is still mostly valid as an optimization pass before porting:

- Merge `skill-help`, `skill-audit`, and `find-skills` into one skill-management surface.
- Merge `pr`, `ship`, and `hotfix` into one delivery surface.
- Consider merging `kickoff` and `execute-prd` behind modes if governed artifact behavior is preserved.

## Codex Canonical Constraints

These are the porting rules that should govern the work:

- Skills are the reusable workflow package: a directory with `SKILL.md`, required `name` and `description`, plus optional `scripts/`, `references/`, `assets/`, and skill-local `agents/`.
- Plugins are the distribution unit for reusable skills and can bundle `skills/`, MCP config, app mappings, hooks, and assets via `.codex-plugin/plugin.json`.
- Custom agents are standalone TOML files under `.codex/agents/` for project scope or `~/.codex/agents/` for personal scope. Each requires `name`, `description`, and `developer_instructions`.
- Codex only spawns subagents when the user explicitly asks for subagents or the parent workflow is explicitly instructed to do so. Ported skills must not assume implicit fan-out.
- `AGENTS.md` is the persistent project instruction layer. It is not a skill and should not become a grab bag for workflow details.
- Codex docs do not currently define a Copilot-style first-class `.prompt.md` repository asset. Prompt material should live as skill instructions, skill-local `references/` or `prompts/` files, agent `developer_instructions`, or plugin `interface.defaultPrompt` starter prompts.
- Hooks belong in Codex lifecycle config through `<repo>/.codex/hooks.json`, `<repo>/.codex/config.toml`, or plugin `hooks/hooks.json`.
- Command execution policy belongs in `.codex/rules/*.rules` or user/global rules, not inside skill prose alone.

## Target Repository Shape

Use a clean Codex source tree instead of mixing generated assets into `claude/`:

```text
codex/
  README.md
  AGENTS.md
  plugins/
    savviety-workflows/
      .codex-plugin/
        plugin.json
      skills/
        <skill-name>/
          SKILL.md
          references/
          scripts/
          assets/
          prompts/
      hooks/
        hooks.json
        scripts/
      assets/
  agents/
    review-explorer.toml
    review-worker.toml
    docs-researcher.toml
    plan-implementer.toml
    plan-reviewer.toml
    plan-fixer.toml
  prompts/
    README.md
    delivery.md
    review.md
    requirements.md
  templates/
    AGENTS.starter.md
    config.toml
    rules/
      delivery.rules
      dependency-install.rules
```

Deployment mapping should eventually extend `manifest.json`:

- `codex/plugins/savviety-workflows` -> repo marketplace plugin source.
- `codex/agents/*.toml` -> `.codex/agents/*.toml` for project-scoped custom agents.
- `codex/templates/AGENTS.starter.md` -> `AGENTS.md` only if absent.
- `codex/templates/config.toml` -> `.codex/config.toml` as shared/updateable if this repo owns it.
- `codex/templates/rules/*.rules` -> `.codex/rules/*.rules`.

## Asset Classification

### Keep as Codex Skills

Port these as user-facing skills with mostly direct rewrites:

- `audit-existing`
- `changelog`
- `checkpoint`
- `code-investigate`
- `code-review`
- `code-review-professional`
- `configure`
- `dep-audit`
- `dep-migrate`
- `env-check`
- `execute-plan`
- `execute-prd`
- `ideate`
- `k8s-verify`
- `parallel-optimization`
- `postmortem`
- `prd-acceptance`
- `prd-validate`
- `process-tune`
- `repo-status`
- `review-adversarial`
- `review-gauntlet`
- `ship`
- `spec-review-adversarial`
- `sync-main`
- `test-plan`
- `thesis`
- `triage`
- `ubiquitous-language`
- `validate-plan`
- `what-is-it-about`
- `work-item`

### Merge Before or During Port

Use the existing consolidation plan, adjusted for current files:

- `skill-help` + `skill-audit` + `find-skills` -> `skills`
- `pr` + `ship` + `hotfix` -> `ship`
- `kickoff` + `execute-prd` -> either `execute-prd` modes or a new `execute` skill

Do not merge these yet:

- `code-review`, `review-adversarial`, `review-gauntlet`, and `code-review-professional`; they are different review modes.
- `triage` and `code-investigate`; one investigates a bug path, the other produces search reports.
- `checkpoint`; it is a primitive called by delivery workflows.

### Convert to Skill References

Keep hidden contracts as skill-local or shared references rather than user-invokable skills unless Codex starts supporting hidden skill metadata:

- `_internal/aers-readiness` -> `skills/prd-validate/references/aers-readiness.md`, also copied into spec and acceptance skills where needed, or centralized under a shared `workflow-foundations` skill.
- `_internal/dependency-classification` -> `skills/test-plan/references/dependency-classification.md`.
- `_internal/disposition` -> `skills/execute-plan/references/disposition.md`.
- `_internal/pre-flight-check` -> `skills/configure/references/pre-flight-check.md`.
- `_internal/professional-rubric` -> `skills/code-review-professional/references/professional-rubric.md`.
- `_internal/repo-delivery` -> `skills/ship/references/repo-delivery.md` and `skills/execute-plan/references/repo-delivery.md`.
- `_internal/security-quick-check` -> `skills/checkpoint/references/security-quick-check.md` and `skills/ship/references/security-quick-check.md`.

### Convert to Custom Agents

Create top-level Codex custom agents only for reusable roles. Keep single-workflow role text inside the skill where it is private.

Reusable custom agents:

- `review-explorer.toml`: read-only codebase mapping and evidence gathering.
- `review-worker.toml`: correctness/security/test/maintainability review findings.
- `docs-researcher.toml`: documentation/API verification using docs MCP when configured.
- `plan-implementer.toml`: bounded implementation worker for parallel plan lanes.
- `plan-reviewer.toml`: lane reviewer after implementation.
- `plan-fixer.toml`: fresh fix worker for specific findings.

Skill-local prompt/reference files:

- `execute-plan/agents/implementer.md`
- `execute-plan/agents/reviewer.md`
- `execute-plan/agents/fixer.md`
- `test-plan/analysts/*`
- `test-plan/test-writer`

The rule is reuse: if a role is used by more than one skill or useful for user-directed delegation, make it `.codex/agents/*.toml`; otherwise keep it skill-local.

### Convert Claude Hooks and Settings

Port `claude/infra/` to plugin hooks and rules:

- `pr-guardrail` -> `hooks/scripts/pr-guardrail.sh` plus `hooks/hooks.json` `PreToolUse` matcher for Bash.
- `journal` -> likely `SessionStart`, `UserPromptSubmit`, and `Stop` hooks after adapting input/output JSON shape.
- `install-scan` -> `PostToolUse` hook for package-manager commands; pair with a `.codex/rules/dependency-install.rules` prompt rule for higher-risk installers.
- `claude/settings.template.json` -> `.codex/config.toml`, `.codex/hooks.json`, and `.codex/rules/*.rules`.

Hook scripts need an adapter pass because Codex hook stdin/stdout schemas differ from Claude's settings and matcher conventions.

## Skill Optimization Rules

Apply these rewrites while porting:

- Keep each `description` short, trigger-heavy, and boundary-heavy because Codex uses descriptions for implicit activation and may truncate skill lists.
- Move long examples, rubrics, schemas, and sample outputs out of `SKILL.md` into `references/`.
- Move shell-heavy repeatable procedures into `scripts/` when they are deterministic and safer as code than prose.
- Replace Claude-specific tool names and slash-command assumptions with Codex-native instructions: `apply_patch`, shell approval escalation, `spawn_agent`, `wait_agent`, and web/docs restrictions where applicable.
- Remove references to `CLAUDE.md` as the only project context source; use `AGENTS.md` and Codex's instruction chain.
- Keep user-specific configuration out of shared skills. Use `configure` plus templates under `assets/` or `templates/`.
- Preserve "fresh subagent per dispatch" semantics, but express them using Codex custom agents and explicit user authorization.
- Replace external model CLI assumptions in `review-adversarial` with either configured MCP/CLI adapters or make the external-review path conditional.

## Prompt Strategy

Codex does not currently have the same top-level prompt asset layer as Copilot. Treat prompts as three things:

- Starter prompts in plugin `interface.defaultPrompt`, for discoverability in install surfaces.
- Reusable task prompts in `codex/prompts/*.md`, documented examples rather than runtime-loaded assets.
- Skill-local `prompts/*.md` files for worker prompt templates that the skill loads only when needed.

Initial starter prompts for the plugin:

- "Use Savviety Workflows to validate this PRD and produce an execution-ready AERS."
- "Use Savviety Workflows to review this branch against main for correctness, security, and missing tests."
- "Use Savviety Workflows to run a checkpoint on the changed packages."
- "Use Savviety Workflows to execute this plan with milestone checks."

## Migration Phases

### Phase 1: Scaffold Codex Platform

Deliverables:

- `codex/README.md`
- `codex/AGENTS.md`
- `codex/plugins/savviety-workflows/.codex-plugin/plugin.json`
- `.agents/plugins/marketplace.json` for local testing
- `codex/templates/config.toml`
- `codex/templates/rules/*.rules`

Acceptance:

- Plugin is visible from the Codex plugin browser after restart.
- A trivial test skill inside the plugin activates explicitly with `$skill`.
- No Claude or Copilot deployment behavior changes.

### Phase 2: Port Low-Risk Standalone Skills

Port skills that do not require subagents, hooks, or external services:

- `audit-existing`
- `validate-plan`
- `repo-status`
- `checkpoint`
- `changelog`
- `ideate`
- `thesis`
- `ubiquitous-language`
- `what-is-it-about`
- `process-tune`

Acceptance:

- Every port has valid YAML frontmatter with `name` and `description`.
- Long reference material is outside `SKILL.md`.
- Skills are invokable explicitly and do not reference Claude-only tools.

### Phase 3: Port Foundation and Configuration Workflows

Port:

- `configure`
- `env-check`
- hidden/internal contracts as references
- config templates
- `work-item` with Linear and ADO branches rewritten for available Codex tools/MCPs

Acceptance:

- Config-dependent skills fail closed with actionable messages.
- No user-specific path, org, project, or token is embedded in shared assets.

### Phase 4: Port Review System

Port:

- `code-review`
- `code-review-professional`
- `review-adversarial`
- `review-gauntlet`
- `spec-review-adversarial`
- shared review references and profiles
- reusable review custom agents

Acceptance:

- `code-review` can run single-agent when the user has not authorized subagents.
- When the user authorizes subagents, review fan-out uses `.codex/agents/*.toml`.
- Findings remain line-cited and severity-ranked.
- External adversarial reviewers are optional/configured, not assumed.

### Phase 5: Port Execution and Delivery

Port:

- `execute-plan`
- `execute-prd` or new consolidated `execute`
- `parallel-optimization`
- consolidated `ship`
- `sync-main`
- `postmortem`
- reusable execution custom agents

Acceptance:

- `execute-plan` is split into a short controller `SKILL.md` plus references for phase details, schemas, and worker templates.
- Parallel lanes require explicit user authorization for subagents.
- Worktree behavior is Codex-safe and never assumes subagents inherit parent environment.
- Delivery command policy is backed by `.codex/rules/*.rules`.

### Phase 6: Port Hooks and Safety Infrastructure

Port:

- PR guardrail
- session journal
- install scan
- rule files for common escalations

Acceptance:

- Hook scripts consume Codex hook JSON on stdin.
- Hook outputs use Codex-supported JSON fields.
- Hook commands resolve from git root, not the caller's current directory.
- Rule files pass `codex execpolicy check` for representative commands.

### Phase 7: Installer and Manifest Integration

Update:

- `manifest.json`
- `cli/skill.sh`
- `docs/repo-skills-design.md`
- root `README.md`

Acceptance:

- `cli/skill.sh --codex --init <target>` installs plugin marketplace, project agents, templates, config, hooks, and rules.
- `cli/skill.sh --codex --update <target>` is safe and never overwrites user-owned `AGENTS.md` or personal config.
- Claude and Copilot install/update paths still behave as before.

### Phase 8: Verification and Regression Tests

Add:

- structural validator for Codex skill frontmatter
- plugin manifest validator
- TOML parser check for custom agents and config
- hook JSON schema smoke test
- installer dry-run test

Acceptance:

- One command validates all Codex assets.
- Sample target repo can install the plugin, list skills, and invoke representative skills.
- All docs and README tables reflect Claude, Copilot, and Codex as separate platforms.

## Initial Priority Order

1. Scaffold plugin and marketplace.
2. Port `validate-plan`, `repo-status`, and `checkpoint` as proof-of-shape.
3. Port `configure` and shared references.
4. Port `code-review` with custom reviewer agents.
5. Split and port `execute-plan`.
6. Port hooks and rules.
7. Extend installer.

## Key Open Questions

1. Should Codex be a first-class platform in `skill.sh` now, or should the first plugin be installed manually until the shape stabilizes?
2. Should hidden contracts be duplicated into each skill's `references/`, or centralized in a `workflow-foundations` skill?
3. Should `execute-prd` and `kickoff` merge before Codex port, or should the port create the new consolidated shape directly?
4. Should `review-adversarial` continue to require external non-Codex model CLIs, or become a configurable optional mode?
5. Should project-scoped custom agents be installed by default, given they can affect subagent selection globally in that repo?
6. How much of `claude/infra/journal` should survive now that Codex has AGENTS.md discovery, session transcripts, hooks, and subagent state?

## Risks

- `execute-plan` is too large to port mechanically. It needs decomposition first or it will become a brittle mega-skill.
- Claude hook scripts will not work unchanged under Codex hook schemas.
- Codex subagents require explicit user authorization in this environment. Skills must degrade cleanly to sequential execution.
- There is no current Codex equivalent to Copilot `.prompt.md` files. Creating a fake first-class prompt layer would add maintenance cost without runtime support.
- Plugin installation caches local plugin content; changes require updating the installed copy or reinstalling/restarting Codex.
