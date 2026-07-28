# Kimi Code CLI Skills Port & Optimization Plan

**Goal:** Bring Claude skills (`claude/`) into the Kimi Code CLI canonical structure under a parallel `kimi/` tree. Port functionality, not form — exploit Kimi's native auto-discovery of `.claude/skills/` so most skills require zero duplication, and add only the thin Kimi-specific layer (agents, AGENTS.md bridge, slash-command alias notes, deploy config).

**Date:** 2026-05-05
**Source:** `claude/` — 39 user-invokable skills + 8 internal rubrics + 3 nested execute-plan worker agents + 3 infra hook bundles
**Target:** `kimi/` — net-new tree

**Naming principle:** Same vocabulary across Claude / Copilot / Codex / Kimi. A developer switching CLIs invokes the same conceptual command and reads the same skill body. Claude's names remain canonical.

---

## 0. The headline insight: Kimi reads `.claude/skills/` natively

As of Kimi Code CLI **v1.39 (2026-04-24)**, `merge_all_available_skills` defaults to `true`. Kimi merges all brand directories (`.kimi/skills/`, `.claude/skills/`, `.codex/skills/`) it finds, at both project and user scope, with priority `kimi > claude > codex`. Skills are also resolved from the nearest `.git` ancestor, not the working directory.

**Practical consequence:** the 39 existing Claude skills already work in Kimi without porting — they get auto-discovered from `.claude/skills/` and surfaced in Kimi's system prompt grouped under `### Project` / `### User`. Frontmatter fields Kimi doesn't recognise (`model: opus`, etc.) are silently ignored.

So the port is **not** "rewrite 39 skills." It is:

1. Add a thin Kimi-native layer for the things that don't auto-port (agents, AGENTS.md, deploy plumbing).
2. Clean up Claude-specific bake-in inside skill bodies that would confuse a Kimi user.
3. Document the user-facing differences (slash command syntax, model selection).
4. Decide how aggressively to mirror the tree.

---

## 1. Canonical Kimi Code CLI structure (2026)

Sourced from the official docs (skills, agents, changelog) — current through v1.41 (2026-04-30).

```
kimi/
├── AGENTS.md.starter                # Auto-injected via ${KIMI_AGENTS_MD}
├── skills/                          # User-invokable + auto-discovered skills
│   └── <skill-name>/
│       ├── SKILL.md                 # Required; name + description frontmatter
│       ├── scripts/                 # Optional executables
│       ├── references/              # Optional sub-content
│       └── assets/                  # Optional supporting files
├── agents/                          # Custom agent YAML files
│   └── <name>.yaml                  # version + agent block
└── templates/                       # Blank user config templates
```

**Format reference (frontmatter for SKILL.md):**

```yaml
---
name: skill-id            # 1-64 chars, lowercase + numbers + hyphens
description: ...          # 1-1024 chars; Kimi reads this to decide whether to load the body
license: optional
compatibility: optional   # ≤500 chars
metadata: { ... }         # optional key-value
type: flow                # optional; "flow" enables embedded Mermaid/D2 workflow diagrams
---
```

**Format reference (Agent YAML):**

```yaml
version: 1
agent:
  name: my-agent
  extend: default               # optional inheritance
  system_prompt_path: ./system.md
  system_prompt_args:           # optional Jinja2 vars
    ROLE_ADDITIONAL: |
      ...
  tools:
    - "kimi_cli.tools.shell:Shell"
    - "kimi_cli.tools.file:ReadFile"
  exclude_tools:
    - "kimi_cli.tools.web:SearchWeb"
  subagents:
    coder:
      path: ./coder-sub.yaml
      description: "Handle coding tasks"
```

**Built-in subagent types** (callable via the `Agent` tool with `subagent_type:`):
- `coder` — general software-engineering task with write access
- `explore` — fast read-only codebase exploration
- `plan` — architecture/design analysis (no write access)

These are **direct analogues** of Claude Code's `general-purpose`, `Explore`, and `Plan` subagent types. Mapping is 1:1.

---

## 2. Format differences, Claude → Kimi

| Concern | Claude | Kimi | Action |
|---|---|---|---|
| Skill discovery dir | `.claude/skills/` | `.kimi/skills/` (also reads `.claude/skills/`) | Deploy to both via manifest |
| Slash invocation | `/<name>` | `/skill:<name>` (or `/flow:<name>` for flow type) | Document; no source change required |
| `model: opus` frontmatter | Honored | Ignored | Strip on port (cosmetic; not breaking) |
| Subagents | Markdown `agents/*.md` with frontmatter | YAML files matching schema | Convert `execute-plan/agents/*.md` |
| Subagent dispatch | `Agent` tool, `subagent_type` param | Same `Agent` tool, same `subagent_type` param, same `coder`/`explore`/`plan` types | No body changes needed |
| Project instruction file | `CLAUDE.md` | `AGENTS.md` (auto-injected as `${KIMI_AGENTS_MD}`) | Bridge file; same convention as Codex |
| Personal/local file | `CLAUDE.local.md` | `~/.kimi/AGENTS.md` (user-level) | Add starter |
| Built-in tool names | `Read`/`Write`/`Edit`/`Grep`/`Glob`/`Bash` | `kimi_cli.tools.file:ReadFile`/etc. — but only matters in agent YAML | Translate inside agent files only |
| Hooks | `.claude/settings.json` hooks block | `.kimi/hooks.json` (similar shape) | Re-emit infra hooks for Kimi |
| Flow workflows | Implicit step-by-step prose | Optional `type: flow` with embedded Mermaid/D2 + BEGIN/END nodes | **Opportunity** — see §6 |
| Skill body refs to "Claude Code" | Common | Confusing | Sweep + neutralise |

**No equivalent in Kimi (skip):**
- `model: opus` / `model: haiku` (Kimi has no per-skill model selection; agent-level model is set at `Agent` tool call time)
- `user-invocable: false` (Kimi doesn't gate skill visibility this way; instead, callable rubrics live as `references/` content inside a parent skill)
- `superpowers:*` cross-skill references (Kimi has no equivalent registry; rewrite as inline guidance or as Kimi skill cross-refs)

---

## 3. Strategy decision — three options

### Option A: **Pure auto-discovery** (zero new tree)

Rely on Kimi reading `.claude/skills/`. Add only a manifest entry that deploys CLAUDE.md as AGENTS.md and ships a `.kimi/config.toml` if needed.

- **Pro:** zero duplication, single source of truth, every Claude fix lands in Kimi automatically.
- **Con:** Kimi users see Claude-flavored prose ("use Claude Code's Agent tool", "TaskCreate"), no Kimi-specific agents, no flow skills, no Kimi-tuned descriptions.

### Option B: **Full parallel tree** (mirror everything)

Mirror `claude/` → `kimi/` 1:1, port every body, maintain in parallel like `copilot-native/`.

- **Pro:** maximum Kimi-nativeness, can take advantage of flow skills and YAML agents fully.
- **Con:** 39 skills × 2 maintenance burden, drift risk, contradicts the `merge_all_available_skills` design intent.

### Option C: **Hybrid overlay** ← **recommended**

Keep `claude/` as the source of truth for skill bodies. Add a `kimi/` overlay that contains only:

- `agents/*.yaml` — the 3 execute-plan workers + any new Kimi-only agents, in YAML
- `AGENTS.md.starter` — Kimi project-instruction file (mirrors `CLAUDE.starter.md` content)
- `templates/` — Kimi-specific config templates (`.kimi/config.toml`, hooks config)
- `infra/` — re-shaped hook bundles that target `.kimi/hooks/`
- A small **compatibility-notes** doc explaining slash-syntax differences

The deploy manifest then ships `claude/` skills into **both** `.claude/skills/` *and* `.kimi/skills/`, so:
- Kimi v1.39+ users with `merge_all_available_skills = true` see them once (deduped by name, kimi-priority).
- Kimi users on older versions or who set the merge flag false still see them via `.kimi/skills/`.
- Claude users are unaffected.

**Selected: Option C.** It matches the pattern already established by `codex/` and `copilot-native/` (parallel-but-thin) and avoids re-authoring 39 skill bodies.

---

## 4. Phased work plan

### Phase 0 — Repo scaffolding (1 PR)

- [ ] Create `kimi/` tree skeleton: `agents/`, `templates/`, `infra/`, `README.md`.
- [ ] Add `kimi/README.md` documenting the structure, auto-discovery model, slash-command syntax, and the "Claude is source of truth" rule.
- [ ] Update root `README.md` "Platforms" table to add a Kimi row.
- [ ] Update `manifest.json` with a `kimi` block:
  ```jsonc
  "kimi": {
    "skills": { "from": "claude", "to": ".kimi/skills",
                "skip": ["README.md", "MODEL-POLICY.md", "SESSION-CONTEXT.md",
                         "settings.template.json", "infra"],
                "preserve_subdirs": ["_project", "_local"] },
    "trees": [
      { "from": "kimi/agents", "to": ".kimi/agents" },
      { "from": "kimi/templates", "to": ".kimi/templates" }
    ],
    "extras": [
      { "from": "kimi/infra/install-scan",  "to": ".kimi/install-scan" },
      { "from": "kimi/infra/journal",       "to": ".kimi/journal" },
      { "from": "kimi/infra/pr-guardrail",  "to": ".kimi/pr-guardrail" },
      { "from": "kimi/templates/config.toml", "to": ".kimi/config.toml" },
      { "from": "kimi/templates/hooks.json",  "to": ".kimi/hooks.json" }
    ],
    "starters": [
      { "from": "kimi/templates/AGENTS.starter.md", "to": "AGENTS.md" }
    ],
    "gitignore": [ ".kimi/journal/*.md", ".kimi/SESSION.md" ]
  }
  ```
- [ ] Update `cli/skill.sh` to handle the `kimi` block (should be a parallel branch of the existing copilot/codex installer logic).
- [ ] Add `kimi-port-plan.md` (this file) to repo.

**Exit criteria:** `cli/skill.sh install --target kimi` no-ops cleanly; `kimi/README.md` is reviewed.

---

### Phase 1 — Skill body cleanups (1 PR, applied to `claude/`)

These improve Claude *and* Kimi readability. They are not Kimi-specific, but they are prerequisites for Kimi to feel native.

- [ ] **Strip `model: opus` from 14 skills** — Kimi ignores it; Claude already encodes its own routing. Files:
  `code-investigate, configure, dep-migrate, env-check, find-skills, grill-me, ideate, kickoff, prd-validate, repo-status, skill-help, spec-review-adversarial, thesis, triage`.
  *(Counter-arg: leaving these in is harmless. Decide based on whether Claude still needs the hint. Recommend: keep, since Claude routing benefits from it and Kimi ignores unknown frontmatter.)*
- [ ] **Sweep `Claude Code`-specific phrasing** in 5 skills (`configure, pr, skill-audit, skill-help, thesis`) and rephrase to be CLI-neutral where possible. Where the reference is genuinely Claude-only (e.g., `superpowers:*`, `TaskCreate`), add a parallel paragraph for Kimi/other CLIs.
- [ ] **Replace inline references to Claude built-in tool names** (`Read`, `Edit`, `Grep`) only where the prose tells the reader to "use the X tool" — replace with the action verb ("read the file", "search for"). The actual model-side tool calls are unaffected because the runtime injects the right tools.
- [ ] **Verify description field for Kimi auto-discovery quality.** Kimi's heuristic is the same as Claude's (description loaded into system prompt; model decides whether to read SKILL.md). The 13 oversized descriptions previously trimmed (per session memory 2026-05-05 18:08) are already in good shape. Spot-check the others.

**Exit criteria:** `validate-skills` passes; description quality holds across both platforms; manual test of 3 random skills under Kimi shows them being discovered and invoked correctly.

---

### Phase 2 — Subagent port investigation (resolved without YAML conversion)

**Original plan:** convert `claude/execute-plan/agents/{implementer,reviewer,fixer}.md` to `kimi/agents/*.yaml` + system-prompt pairs.

**Outcome after closer inspection:** **no conversion needed.**

These three files are not independent agents. They are **prompt templates with `{PLACEHOLDER}` substitution** — `{TEAM_NAME}`, `{WORKTREE_PATH}`, `{PLAN_SHA}`, `{WRITE_SCOPE}`, `{BUILD_CMD}`, etc. — that the parent `execute-plan` skill substitutes at dispatch time. Wrapping them in Kimi `version: 1` agent YAML and pointing `system_prompt_path` at one would ship a system prompt full of raw placeholders, which is broken.

Kimi handles this correctly with zero porting:
- `execute-plan` (auto-discovered from `.claude/skills/`) substitutes the placeholders.
- It then calls the `Agent` tool with the substituted prompt as the `prompt` parameter.
- It selects the right built-in subagent type — Kimi's `coder` for implementer/fixer, optionally `explore` for the reviewer's read pass.

What we did instead:
- Documented the subagent-type mapping (`general-purpose`/`Explore`/`Plan` → `coder`/`explore`/`plan`) in `kimi/agents/README.md`.
- Documented when to actually add a YAML agent here (only when the system prompt is fully-specified with no placeholders, AND someone wants to launch it via `--agent-file` directly).

**Exit criteria met:** `execute-plan` runs end-to-end under Kimi via auto-discovery; subagent dispatch routes through Kimi's built-in `coder`/`explore`/`plan` types automatically.

---

### Phase 3 — AGENTS.md bridge + project instructions (1 PR)

Kimi auto-injects `${KIMI_AGENTS_MD}` from project `AGENTS.md`. CLAUDE.md does **not** auto-load in Kimi (same gap Codex hit).

- [ ] Create `templates/AGENTS.starter.md` that mirrors `templates/CLAUDE.starter.md` with the cross-CLI sections only (Build/Test/Ship commands, conventions, project context). Strip Claude-specific blocks (Skill tool guidance, etc.).
- [ ] Document in `kimi/README.md` that AGENTS.md is the canonical Kimi project file and is shared with Codex.
- [ ] Optionally: add a `templates/AGENTS-CLAUDE-bridge.md` that's a one-liner `@CLAUDE.md` include if both files coexist — only useful if a project mixes CLIs.

**Exit criteria:** A project deployed for both Claude and Kimi has consistent project rules without duplicating prose.

---

### Phase 4 — Infra (hooks) port — **shipped with TODOs**

`claude/infra/{install-scan, journal, pr-guardrail}` are shell-script bundles wired into `.claude/settings.json` hooks.

**Discovery during the port:** Kimi does **not** use a separate `hooks.json` — hooks are inline `[[hooks]]` TOML arrays inside `~/.kimi/config.toml` (per the official docs). This changed the shape of the implementation:

- Hook scripts are **single-sourced from `claude/infra/`** rather than mirrored to `kimi/infra/` — they're pure shell with no Claude-API dependency, and avoiding duplication keeps maintenance honest.
- The deploy manifest pulls extras directly from `claude/infra/<bundle>/` into `<target>/.kimi/<bundle>/`.
- Hook event wiring lives in `kimi/templates/config.toml` as commented-out `[[hooks]]` blocks. The user uncomments after verifying script behavior under Kimi's hook stdin format (Kimi passes JSON on stdin including `cwd`, `session_id`, `hook_event_name` — the scripts were authored to read `$CLAUDE_PROJECT_DIR` and Claude's stdin shape, so they may need adjustment).

**Done:**
- [x] Manifest extras point at `claude/infra/{install-scan,journal,pr-guardrail}` → `.kimi/<bundle>/`.
- [x] `kimi/templates/config.toml` ships with `[[hooks]]` block scaffolding for all three bundles, commented out by default.
- [x] User-facing README and AGENTS.md note the TOML-not-JSON convention.

**TODO (deferred until a Kimi user actually runs these hooks):**
- [ ] Confirm Kimi's `Shell` matcher class name and that the scripts trigger on the correct event payloads.
- [ ] Adjust scripts to read JSON-from-stdin style (`jq -r .cwd`) instead of `$CLAUDE_PROJECT_DIR` if needed.
- [ ] If Kimi grows a native session-journal mechanism, drop the journal hook bundle and update README.

**Exit criteria met:** Install scan / PR guardrail / journal scripts deploy into `.kimi/`. The TOML wiring scaffolds are in place. End-to-end firing under Kimi requires real-Kimi validation that we can't do from inside Claude Code.

---

### Phase 5 — Optional: flow-skill conversions (later, 1 PR per skill)

Kimi's `type: flow` lets you embed a Mermaid diagram with `BEGIN` / `END` nodes and let the agent walk decision branches via `<choice>branch</choice>` markers. Several Claude skills have implicit flow shapes that would benefit:

| Candidate skill | Why a flow fits |
|---|---|
| `kickoff` | Already a multi-phase pipeline (readiness → plan → implement → review) |
| `execute-plan` | Per-task loop with reviewer/fixer fan-out is a textbook flow graph |
| `triage` | Decision-tree-shaped: classify, then route |
| `code-review` | 11-domain dispatch with conditional triggers (data-integrity, api-contract) maps cleanly to a flow with branch nodes |
| `hotfix` | Linear flow with a branch on test pass/fail |

This is purely upside — flow-typed skills can also be invoked via `/skill:<name>` if the user wants the prose form. **Defer** these until Phases 0–4 land and we have actual Kimi usage data to prioritise.

**Exit criteria (per candidate):** Mermaid diagram renders in Kimi; agent successfully walks at least one branch decision; reviewers are happy with the diagram-to-prose ratio.

---

## 5. Skill-by-skill triage

39 skills. None require a body rewrite for Kimi; categorize by what (if anything) needs touching.

### Auto-port, no changes (28 skills)

These work via `.claude/skills/` discovery alone, post-Phase 1 sweep:

`audit-existing, changelog, checkpoint, code-review, code-review-professional, configure, dep-audit, dep-migrate, env-check, find-skills, hotfix, ideate, infra, k8s-verify, parallel-optimization, postmortem, pr, prd-acceptance, prd-validate, process-tune, repo-status, review-adversarial, review-gauntlet, ship, skill-audit, skill-help, spec-review-adversarial, sync-main, test-plan, thesis, triage, ubiquitous-language, validate-plan, what-is-it-about, work-item, grill-me, kickoff, code-investigate`

### Need agent wrappers (1 skill)

- **`execute-plan`** — see Phase 2; 3 worker agents need YAML + system-prompt files.

### Need infra wrappers (3 hook bundles)

- `install-scan`, `infra/journal`, `infra/pr-guardrail` — see Phase 4. (`install-scan` was promoted out of `infra/` since it's a cross-cutting hook used by every CLI.)

### Internal-only (8, no port required)

`_internal/aers-readiness, closed-decisions, dependency-classification, disposition, pre-flight-check, professional-rubric, repo-delivery, security-quick-check` — these are sub-skill content callable from parent skills, not user-invokable. Auto-discovered with everything else.

---

## 6. User-facing differences worth documenting

Land these in `kimi/README.md` so users aren't surprised:

| Difference | Claude | Kimi |
|---|---|---|
| Slash invocation | `/code-review` | `/skill:code-review` |
| Model override per skill | `model: opus` in frontmatter | Pass `model:` to the `Agent` tool at dispatch time |
| Project instruction file | `CLAUDE.md` | `AGENTS.md` |
| Subagent types | `general-purpose`, `Explore`, `Plan` (+ skill-shipped) | `coder`, `explore`, `plan` |
| Personal overlay | `CLAUDE.local.md` | `~/.kimi/AGENTS.md` |
| Permission gating | `.claude/settings.local.json` | `.kimi/config.toml` (`allowed_tools`, hooks) |
| Discovery scopes | implicit user vs project | explicit `### Project` / `### User` / `### Extra` / `### Built-in` headings in system prompt |

---

## 7. Open questions for review

1. **Manifest dual-deploy:** should `cli/skill.sh` deploy `claude/` skills to `.kimi/skills/` *and* `.claude/skills/`, or rely solely on Kimi's `merge_all_available_skills` to read from `.claude/skills/`? Recommend deploying to both — handles users with non-default merge config and is unambiguous for tool-version compatibility.
2. **AGENTS.md ownership:** does Kimi share AGENTS.md with Codex (which already uses it)? They appear to have the same convention; users running both CLIs would benefit from one file. Confirm via Kimi changelog before finalising.
3. **Flow-skill scope:** how many of the 5 flow candidates (§4 Phase 5) are worth converting upfront vs. wait-and-see? My instinct is convert `kickoff` and `execute-plan` first (they're the highest-value pipelines) and defer the rest.
4. **`ideate model: opus` and friends:** keep the field for Claude routing benefit, or strip for hygiene? Recommend keep — Kimi ignores it, Claude uses it.
5. **Hooks naming convergence:** `.claude/install-scan/`, `.codex/install-scan/`, `.kimi/install-scan/` will all coexist on a multi-CLI repo. Acceptable noise or do we want a `.shared/install-scan/` symlinked from each? Recommend acceptable noise — three small dirs with identical contents is cheaper than introducing a new shared layout.

---

## 8. Effort estimate

| Phase | Scope | Estimate |
|---|---|---|
| 0 — Scaffolding | Tree, manifest, README, skill.sh wiring | 1 session |
| 1 — Skill body cleanups | Frontmatter sweep, Claude-specific phrasing | 1 session |
| 2 — Subagent port | 3 YAML files + 3 system-prompt files for execute-plan | 0.5 session |
| 3 — AGENTS.md bridge | Starter file + docs | 0.5 session |
| 4 — Infra port | hooks.json + config.toml + 3 bundles | 1 session |
| 5 — Flow skills (optional) | Per skill | 1 session per skill |

**Total core port (Phases 0–4):** ~4 sessions. Comparable to the Codex port effort.

---

## 10. Phase 6 — Native Kimi plugin (completed 2026-07-17)

The 2026-05-05 hybrid overlay was upgraded to a native Kimi plugin while keeping `claude/` as the prose source of truth.

### Delivered

- `kimi/kimi.plugin.json` — plugin manifest packaging skills, commands, and session-start guidance.
- `claude/gh-readiness/SKILL.md` — read-only skill that verifies `gh` is installed, authenticated, and able to reach the GitHub API before PR/issue/release workflows.
- `kimi/skills/` — generated from `claude/` by `bin/build-kimi-plugin` with native frontmatter:
  - `whenToUse` on every skill
  - `type: flow` on multi-phase pipeline skills
  - `arguments` on parameterized skills
  - `model:` frontmatter stripped (Claude-only)
  - Body slash references rewritten to `/skill:<name>`
- `kimi/commands/` — plugin slash commands for the most common manual invocations (`review`, `plan`, `checkpoint`, `ship`, `triage`, `status`).
- `kimi/hooks/` — Kimi-aware hook adapters for `install-scan`, `pr-guardrail`, `journal`, and `gh-auth-guard` (blocks `gh pr/issue/release create` when `gh` is missing or unauthenticated).
- `bin/build-kimi-plugin` — idempotent build script with `--check` for CI.
- Updated `manifest.json` and `cli/skill.sh` to deploy the plugin tree plus project-level hook wiring.
- Updated `kimi/templates/config.toml` with inline `[[hooks]]` scaffolding pointing at the new adapters.

### Design notes

- **No custom agent YAMLs were added.** The existing `execute-plan/agents/*.md` files are prompt templates with runtime `{PLACEHOLDER}` substitution, not standalone agents. They continue to work via Kimi's built-in `coder` / `explore` / `plan` subagent types.
- **Plugin hooks were omitted from `kimi.plugin.json`.** Kimi plugins run hooks from the per-user plugin root and cannot reliably reference project-level scripts. Project-level hooks remain configured via `.kimi/config.toml` after `cli/skill.sh --kimi --init`.

### Missing plugins / native addins to add value

| Add-in | Where it fits |
|---|---|
| **GitHub MCP server** | Optional alternative to `gh` CLI; current skills already use `gh` for `/pr`, `/issue-slices`, `/bug-session` |
| **Azure DevOps / Linear MCP server** | `/work-item` retrieves and updates tickets |
| **Kubernetes MCP server** | `/k8s-verify` queries cluster state without shelling out |
| **OSV / supply-chain MCP server** | `/dep-audit` CVE and maintainer-risk checks |
| **Semgrep / CodeQL static-analysis MCP server** | `/domain-review` and `/code-review-professional` automated lens |
| **Obsidian / note-taking MCP server** | `/vault` reads/writes notes through MCP tools |
| **Browser / web-fetch MCP server** | `/what-is-it-about` and `/code-investigate` fetch public docs and transcripts |
| **Kimi Datasource plugin** | `/thesis`, `/what-is-it-about`, `/prd-validate` market/domain research |
| **Kimi `/remember`** | Replace deprecated handoff pattern for session continuity across long `/execute-plan` runs |
| **Kimi `/goal` mode** | Run `/kickoff`, `/execute-prd`, `/execute-plan` as autonomous goals with explicit completion criteria |
| **Kimi TUI theme plugin** | Savviety-branded theme for teams rolling out the workflows |

---

## 9. References

- [Agent Skills | Kimi Code CLI Docs](https://moonshotai.github.io/kimi-cli/en/customization/skills.html)
- [Agents and Subagents | Kimi Code CLI Docs](https://moonshotai.github.io/kimi-cli/en/customization/agents.html)
- [Hooks | Kimi Code CLI Docs](https://moonshotai.github.io/kimi-cli/en/customization/hooks.html)
- [Plugins | Kimi Code CLI Docs](https://moonshotai.github.io/kimi-cli/en/customization/plugins.html)
- [Changelog | Kimi Code CLI Docs](https://moonshotai.github.io/kimi-cli/en/release-notes/changelog.html)
- [GitHub - MoonshotAI/kimi-cli](https://github.com/MoonshotAI/kimi-cli)
- [Kimi K2.5 Developer Guide (NxCode, 2026)](https://www.nxcode.io/resources/news/kimi-k2-5-developer-guide-kimi-code-cli-2026)
