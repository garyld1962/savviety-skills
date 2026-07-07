# Native-Overlap Audit — 2026-07-03

**Repo:** /Users/gary/repos/savviety-skills
**Custom skills audited:** 41 (all `claude/<name>/SKILL.md`, excluding skip list and `_internal/`)
**Native catalog:** read live from session at 2026-07-03 (machine: Watson)
**Status:** APPLIED — fixes executed on branch `chore/native-overlap-fixes` (2026-07-04), not committed.

## Scope notes

- **Delta audit.** `native-overlap-20260702.md` ran yesterday on another machine. This
  run independently re-derived the comparison and confirms its verdicts; carried-forward
  findings are one line each below. New findings get full treatment.
- **Catalog drift between machines.** Yesterday's session had the security plugins
  (`supply-chain-risk-auditor`, `differential-review`, `static-analysis`,
  `insecure-defaults`, `variant-analysis`); Watson does not. Yesterday's
  `dep-audit → integrate supply-chain-risk-auditor` verdict is machine-conditional —
  guard any such integration behind an availability check, or install the plugin set
  on both machines.
- **New native functionality that changed verdicts this cycle:**
  - **Workflow tool** — deterministic multi-agent orchestration (`pipeline()`,
    `parallel()`, adversarial-verify / judge-panel patterns, per-agent
    `isolation: 'worktree'`).
  - **Agent tool** background execution, `SendMessage` continuation, native worktree
    isolation; EnterWorktree/ExitWorktree.
  - Built-ins: `/verify`, `/simplify`, `/run`, `/loop`, `/schedule`, `/deep-research`,
    `/code-review` effort levels + `ultra` cloud multi-agent mode, persistent memory.
- **PR #31** (open since 2026-05-19, "add 7 new skills and integrate new Claude
  features") touches four files edited by this audit (`review-gauntlet`, `test-plan`,
  `dep-migrate`, `modernize`) plus `kickoff`, `prd-validate`, `process-tune`,
  `code-investigate`, and adds `/goal`, `/feature-sweep`, `bug-session`,
  `design-twice`, `issue-slices`, `refactor-brief`, `vault`. It will need a rebase
  against this branch; reconcile its "new Claude features" scope against the
  Workflow-integration edits below before merging either.

## Operator decisions (2026-07-04)

1. **BuildFlow user-level skills dismissed.** `~/.claude/skills/` contains 7 BuildFlow
   project skills (`checkpoint`, `code-review`, `review-api/db/design/tests`, `teams`)
   that shadow this repo's `checkpoint`/`code-review` in every session on Watson.
   Operator: they are old and will be overwritten — no relocation.
2. **Rename approved:** `code-review` → `domain-review`.
3. **All fix batches approved:** cleanup, tighten/cross-reference edits,
   Workflow-tool integrations, plugin installs.

## Applied changes

### Rename: `claude/code-review` → `claude/domain-review`

Resolves the collision with the built-in `/code-review` (effort levels, `--fix`,
`ultra`). Applied:

- `git mv claude/code-review claude/domain-review`; frontmatter `name:` updated;
  description now opens with the rename note and a "Preferred over the built-in
  /code-review when…" claim.
- All `/code-review` invocations and bare skill-name references across `claude/`
  updated (protected: `code-review-professional`, `superpowers:requesting-code-review`,
  generic "code review" prose, historical docs under `docs/`).
- Repo tooling updated: `.claude/skills/new-domain/SKILL.md`,
  `.claude/skills/validate-skills/SKILL.md` (path refs `claude/code-review/` →
  `claude/domain-review/`), `kimi/README.md` invocation example,
  `claude/execute-plan/SKILL.md` `code-review-profile` key → `domain-review-profile`
  (key used nowhere else).
- **Not touched:** `codex/` and `copilot/` trees (independent ports — manual parity
  work, see COPILOT-NATIVE-PARITY.md); historical docs/decks.

### Cleanup

- Deleted `claude/execute-workflow/` (empty since April — only `.DS_Store`).

### Tighten / cross-reference edits (per-pair verdicts)

| Skill | Native counterpart | Verdict | Edit applied |
|---|---|---|---|
| `triage` | `superpowers:systematic-debugging` | Tighten | Description claims report-without-fix niche; When NOT defers drive-to-fix sessions |
| `grill-me` | `superpowers:brainstorming` | Tighten | Description claims post-draft challenge niche; added When NOT to Use section (brainstorming, /ideate) |
| `test-plan` | `superpowers:test-driven-development` | Cross-reference | Description states composition (stubs vs red/green loop); fixed stale `/review-tests` ref → `/domain-review` (tests domain) |
| `review-adversarial` | built-in `/code-review ultra` | Hand off | When NOT: same-model cloud scale → ultra; cross-model challenge stays here |
| `pr` | `superpowers:finishing-a-development-branch` | Hand off | When NOT: merge/PR/discard decision → superpowers, mechanics stay here |
| `ship` | `superpowers:finishing-a-development-branch` | Hand off | Same pattern |
| `dep-migrate` | `vercel:next-upgrade` | Hand off (narrow) | When NOT: Next.js upgrades with Vercel plugin available |
| `modernize` | official `code-modernization` plugin | Tighten | When NOT: generic legacy modernization → plugin; AI-time refresh + /execute-prd handoff stays here |
| `checkpoint` | built-in `/verify`, `superpowers:verification-before-completion` | Integrate | Description marks static-gates-only; When NOT routes runtime proof to /verify |
| `prd-acceptance` | built-in `/verify` | Integrate as sub-primitive | `behavior` verification method now prefers invoking /verify for runtime criteria |

### Workflow-tool integrations

| Skill | Edit applied |
|---|---|
| `execute-plan` | Phase 2.7a harness note: prefer native `isolation: 'worktree'` over manual `git worktree add`; install + base-SHA steps unchanged; manual mechanics remain the fallback |
| `parallel-optimization` | Required Plan Section now documents the mechanical mapping: lane → `agent()` with worktree isolation, barrier → `parallel()` join, wave → `pipeline()` stage |
| `review-gauntlet` | Step 3 runs the three lenses as independent parallel subagents (Workflow `parallel()` or single-message Agent dispatch), sequential as fallback; When NOT defers external-feedback decisions to `superpowers:receiving-code-review` |

## Confirmed no-overlap

`changelog`, `audit-existing`, `hotfix`, `sync-main`, `env-check`, `k8s-verify`,
`configure`, `postmortem`, `process-tune`, `prd-validate`, `spec-review-adversarial`,
`validate-plan`, `thesis`, `ubiquitous-language`, `what-is-it-about`, `work-item`,
`code-review-professional` (craft/seniority grading has no native counterpart),
`drawio` (already cross-references `create-diagram`), `code-investigate` (repo-scoped;
`deep-research` is web-scoped), `ideate` and `kickoff` (already exemplary
cross-referencers), `repo-status`, `skill-audit`, `skill-help`, `dep-audit`,
`execute-prd` (existing preferred-over claim suffices), `find-skills` (yesterday's
Redundant-pending-verification verdict stands, unverified this cycle).

## Marketplace gap analysis (researched 2026-07-03, GitHub API verified)

### Ecosystem shift

The official marketplace moved to **`anthropics/claude-plugins-official`** (31.5k★,
255 plugins, auto-registered in Claude Code). The legacy in-repo
`anthropics/claude-code` marketplace (13 plugins) is superseded.
`anthropics/skills` (157.9k★) remains the Agent Skills reference repo (17 skills).

### Recommended installs (not currently on Watson)

| Plugin | Why | Caution |
|---|---|---|
| `typescript-lsp`, `pyright-lsp` | New official LSP plugin class — diagnostics/navigation; repo work is TS-centric | none |
| `security-guidance` | Edit-time security warnings + LLM diff review; complements `/dep-audit`, built-in `/security-review` | none |
| `hookify` | Generates custom hooks; pairs with the repo's session-state hooks | none |
| `plugin-dev`, `mcp-server-dev` | Official toolchain for skill/plugin authoring — this repo's core activity | none |
| `pr-review-toolkit`, `feature-dev` | Strong official dev-workflow plugins | Install only now that the `domain-review` rename removes the review-name collision |
| security plugin set (Sherlock parity) | `supply-chain-risk-auditor` etc. — unblocks yesterday's `dep-audit` integration verdict | none |

From `anthropics/skills`: `webapp-testing` (Playwright-driven) if web-UI testing
becomes routine; document skills (docx/pdf/pptx/xlsx) low value for this repo.

### Third-party, high adoption (verified star counts)

- **obra/superpowers** (245.3k★, v6.1.1) — installed; now also in the official
  marketplace: consider switching install source to `superpowers@claude-plugins-official`.
- **multica-ai/andrej-karpathy-skills** (187.2k★) — single CLAUDE.md of LLM-coding
  priors; global CLAUDE.md already covers most of it — diff, don't install.
- **wshobson/agents** (37.5k★) — multi-harness plugin marketplace (~72 plugins);
  useful convention reference for `port-skill` (`wshobson/commands` is dormant,
  merged in).
- **sickn33/antigravity-awesome-skills** (42.3k★, 1,800+ skills) and
  **davila7/claude-code-templates** (28.4k★, aitmpl.com) — search sources for
  `/find-skills` / `/skill-audit`, not bulk installs.
- **ericbuess/claude-code-docs** (947★) — local docs mirror + `/docs` command; small,
  high utility.
- **skillsmp.com** — de-facto community index (2M+ indexed skills, free API + MCP
  server); candidate search backend for `/find-skills`.

## Follow-ups (not applied)

1. Rebase or close **PR #31**; reconcile its feature-integration scope with this
   branch's Workflow edits.
2. **Pre-existing stale refs in `new-domain`:** `claude/domain-review/README.md` and
   `claude/domain-review/tests/validate-structure.sh` are referenced but do not exist
   in the tree. Pre-existing breakage, out of this audit's scope — fix separately.
3. Port the `domain-review` rename to `codex/` and `copilot/` trees (parity log).
4. Install the security plugin set on Watson for Sherlock parity.
5. Verify `find-skills` against the upstream marketplace skill before deprecating.
