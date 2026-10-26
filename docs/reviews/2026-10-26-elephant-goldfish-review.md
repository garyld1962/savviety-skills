# Review: savviety-skills against elephant-goldfish (2026-10-26)

Scope: the `claude/` tree of this repo, its shared contracts and runtime
(`run-plan.mjs`), and the sibling `~/repos/elephant-goldfish` repo (Claude,
Codex and Gemini adapters, five `eg-*` commands, bootstrap procedure). This is a
source review; nothing was run live.

Part 1 records the independent analysis, written before reading any plan.
Part 2 compares it with `docs/plans/elephant-goldfish-enhancements.md` and
gives the combined recommendation. The appendix records a side comparison
with `docs/plans/2026-09-10-claude-plugin.md`, which was read first by
mistake and turned up one finding worth keeping.

---

## Part 1 — Independent analysis

### 1.1 What the two repos are

| | savviety-skills | elephant-goldfish |
|---|---|---|
| Unit | 50 user-invocable skills + 12 `_internal` contracts, 5 platforms | 5 commands, 3 platforms |
| Install model | Single-source tree copied by an installer; repo declares a `CLAUDE.md ## Commands` contract; skills stay environment-neutral | Templates fetched via `gh api` and **rewritten per repo** (`[BOOTSTRAP: …]` markers replaced with concrete lint/test/dev-server commands) |
| Independence lever | **Cross-model** (`/review-adversarial` runs Codex/Gemini) | **Cross-context** (a fresh subagent that sees only the artifact, never the session's intent) |
| Governance | Plan-format contract, readiness scoring, disposition vocabulary, postmortem taxonomy, Workflow-tool runtime | Prose protocol: ledger, fix-or-rebut verbatim, hard round caps, mandatory `AskUserQuestion` gates |
| Entry points | Many, overlapping (goal/thesis/ideate/grill-me/design-twice upstream; kickoff/execute-prd/execute-plan middle; triage/bug-session/hotfix for bugs) | "You have X → start with Y → you get Z" table, one diagram |

The two designs are not competitors. elephant-goldfish is a *review protocol*;
savviety-skills is a *delivery system*. The protocol can be slotted into the
system without copying the per-repo rewriting model, which conflicts with this
repo's single-source philosophy (`docs/Philosophy.md` § "Source of truth
matters").

### 1.2 Recommendations (ranked)

#### R1 — Add a context-asymmetry ("blind reviewer") contract and use it at the review seams

**Observation.** Every reviewer in this repo is *told what the author was
trying to do*: `run-plan.mjs` passes `Intent: ${plan.intent}` and
`pr_description` to the breakpoint and PR-boundary reviews; `/review-adversarial`
Step 2 states the intent to each lens; `/domain-review` carries
`pr_description` into the worker context header. elephant-goldfish's central
claim is that a reviewer who knows the intent reads the diff *as the author
intended it*, and that the cheapest correctness signal is a reader who does
not. `docs/Philosophy.md` already names "Independence improves review quality"
as a belief, but the only independence mechanism shipped is model diversity,
which needs a second CLI and is skipped silently when absent.

**Recommendation.** Add `claude/_internal/blind-review/SKILL.md`
(`user-invocable: false`, `kind: reference`) that defines:

- what a blind reviewer receives (diff range or document, repo access, the
  `CLAUDE.md` conventions) and what it must not receive (plan intent, task
  body, prior-round reasoning, the orchestrator's hypothesis);
- the exact-template rule (prompt body passed verbatim; only a declared focus
  slot may be filled);
- the re-review rule for fix rounds (full template again, plus a "previous
  round's fixes — verify each, and look for issues introduced by the fixes"
  addendum);
- the convergence trip (a new finding at the same `file:method` as a
  previously fixed one, or round N of the cap, ends the loop and escalates).

Then consume it in three places:

1. `run-plan.mjs` `reviewGate`: run the breakpoint review blind by default
   (drop `Intent:` from the prompt; keep it for the `full` domain-review pass,
   which is explicitly intent-aware craft review). One flag,
   `flags.blindReview`, so the behaviour is visible in the report.
2. `/review-adversarial`: add a `--blind` variant. Cross-model *and*
   cross-context is strictly stronger than cross-model alone, and `--blind`
   gives the skill a useful degraded mode when no opposite-model CLI exists
   (today it skips entirely in auto mode).
3. `/domain-review`: make `pr_description` opt-in from the caller rather than
   the default, and note in the worker header whether the review is blind.

**Why first.** It is the single idea in elephant-goldfish that this repo
lacks, it costs nothing extra at runtime, it works on all five platforms, and
it is independent of the plugin packaging work.

#### R2 — Independent diagnosis before any fix (`/triage`, `/hotfix`)

**Observation.** `/triage` is a one-context investigation that ends in a
report; `/hotfix` has a "confirm scope" step but relies on the same context
that formed the hypothesis. `eg-fix-bug` writes the hypothesis down, *hides
it*, hands symptom + repro to a fresh `Explore` agent, then records
convergence or divergence. Divergence is the cheapest anchoring detector
available.

**Recommendation.**

- `/triage`: after Step 4 (root cause), spawn one blind diagnosis agent with
  symptom + repro only. Add a `Goldfish agreement: converged | diverged — <why>`
  line to the triage report. Skip when `--quick`.
- `/hotfix`: same check between Step 3 (confirm scope) and Step 4 (apply the
  fix), skippable only when the location is "mechanically obvious" — borrow
  that wording. Hotfix is exactly where anchoring costs the most.
- Record the pattern in the R1 contract so both skills cite one source.

#### R3 — Add an empirical readiness pass ("could a cold implementer ship this without asking?")

**Observation.** Readiness in this repo is rubric-scored by the same context
that wrote the artifact (`_internal/aers-readiness`, `/validate-plan`,
`execute-prd` step 8). `eg-new-feature` Pass C is a different kind of test:
hand the document to a fresh agent and ask it to list every question it would
have to ask before shipping. An empty list is the readiness verdict. That test
catches the ambiguity class `execute-plan` preflight gate 4 exists for
(referent, existing-state, scope-boundary), but *before* the run starts.

**Recommendation.**

- `/validate-plan`: add an optional `--cold-reader` pass (default on when
  invoked from `/execute-prd` step 9) that dispatches one fresh agent with the
  plan file only and the Pass C prompt. Open questions become `plan-ambiguity`
  findings and feed the existing fix-and-revalidate loop (max 3).
- `/spec-review-adversarial`: add a fifth lens, **Readiness** ("first-pass
  implementer, no follow-up questions allowed"). The existing four lenses ask
  whether the spec is *good*; none asks whether it is *executable*.
- Keep the comprehension pass (Pass A) out: `/simplify` and `/humanizer`
  already cover prose clarity, and elephant-goldfish itself treats it as
  informational only.

#### R4 — Close the review-fix loop properly in `run-plan.mjs`

**Observation.** `gateFindings` marks a finding `fixed` on the fixer's own
`status: 'fixed'` and never re-reviews. `reviewGate` turns a missing or failed
review into `[]` (line 258), so a crashed reviewer passes the gate. The
alignment schema requires `allTasksImplemented` but the value is never read
(lines 278–312). All three were raised as **High** in
`docs/reviews/2026-09-04-claude-parity.md` and are still open. elephant-goldfish
does not have a runtime, but its loop shape is the right one: the reviewer, not
the fixer, closes a finding; the loop ends on "no findings AND every prior
finding settled"; rebuttals are surfaced verbatim.

**Recommendation.**

- Null/failed review → throw (same treatment `checkpoint` already gets at
  line 272).
- After the fix cycles for a gate, re-run the reviewer once (blind, per R1)
  with the fixed-findings list; a finding is `fixed` only if that pass does not
  re-raise it. Bound the total at `maxFixCycles`.
- Check `alignment.allTasksImplemented === false` → FAIL with the missing task
  ids.
- Report `disagree-with-evidence` dispositions verbatim in
  `execution-report.md`, matching `_internal/disposition` § "No silent
  dismissals" (add that section; the vocabulary exists, the rule does not).
- While there: `AUTO_ACCEPT` is hard-coded and `adversarial` fires on
  `files >= 10`, but `_internal/repo-delivery` documents
  `auto_accept_deviations`, `adversarial_triggers` (globs) and `retry_budget`
  as the contract. Either read them from `cfg.commands` or stop documenting
  them. The runtime's fallback "run the built-in /code-review at high effort
  instead" also contradicts `/review-adversarial`'s own auto-mode rule (skip
  and record). Pick one.

#### R5 — Interaction gates that survive autonomous-mode directives

**Observation.** The interview skills (`/goal`, `/prd-create`, `/ideate`,
`/grill-me`, `/design-twice`) say "interactive by design" and `/goal` refuses
non-interactive callers, but none says what to do when a session-level
directive says "do not stop for clarifying questions". `execute-prd` and
`kickoff` branch on "interactive operator vs autonomous" without defining how
the mode is detected. elephant-goldfish puts a short, uniform block in every
command: the skill's enumerated gates are protocol, not clarifying questions;
they run regardless; the only opt-out is an explicit phrase in the invoking
turn; even then one named gate is non-negotiable.

**Recommendation.** Add `claude/_internal/interaction-gates/SKILL.md` with:
how to detect autonomous mode (no operator reply possible, `-p`, scheduled
run, workflow subagent); the rule that skill-enumerated gates are protocol;
the opt-out phrase; and a one-paragraph block each skill pastes under its
`## When to Use`. Apply to the five interview skills and to the
interactive-vs-autonomous branches in `execute-prd` step 4, `execute-plan`
gate 4, and `kickoff` step 2. This directly serves Philosophy § "Preserve human
control over consequential decisions".

#### R6 — Infer the `## Commands` contract at init instead of leaving placeholders

**Observation.** `skills --claude --init` writes `templates/CLAUDE.starter.md`
with `lint: <cmd>` placeholders, and every consuming skill halts until they
are filled; `/configure` has no `commands` target in its registry.
elephant-goldfish's bootstrap reads `package.json`, `Gemfile`, `pyproject`,
CI config and `git log`, prints a **stack profile**, asks the user to confirm,
and only then writes. The declared-contract model is right (no heuristic
fallback at runtime); the gap is that nothing helps the user *declare* it.

**Recommendation.** Add a `commands` target to `claude/configure/registry.md`
whose interview step proposes values inferred from manifests and
`.github/workflows/*.yml`, shows the stack profile, and writes the confirmed
`## Commands` block (plus optional `adversarial_triggers`, `runtime_probes`).
Have the installer's init message point at `/configure commands`. Keep the
runtime rule "no inference, halt if absent" unchanged.

#### R7 — Give stack-specific review knowledge a home

**Observation.** The most valuable bootstrap content in elephant-goldfish is
the per-stack "Hunt for" list (Rails N+1 and tenant scoping, Flutter dispose
races, Workers request-scope leaks, DSP allocation in `process()`) and the
per-stack implementation layer order. This repo has the right container
(`domain-review/dialect/*`, `domain-review/platform/*`) but only seven
overlays, and `execute-prd` step 7 has one generic layer order.

**Recommendation.** Two cheap additions: (a) more overlays, starting with the
stacks the Blazor and TS-monorepo templates imply (`dialect/csharp-blazor`,
`platform/efcore`, `dialect/react`, `platform/cloudflare-workers`); (b) an
optional `layer_order:` list in `_internal/repo-delivery` that `execute-prd`
step 7 uses to sequence feature tasks. Both keep knowledge single-sourced
rather than copied into each repo.

#### R8 — Make the entry points legible

**Observation.** 50 skills with a six-step "Typical flow" and a review
decision matrix. A newcomer cannot tell `/kickoff` from `/execute-prd`, or
`/goal` from `/thesis` from `/ideate`, from the README alone.
`docs/consolidation-plan.md` (unified `/skills`, `/execute`, `/ship`) was
written and not executed. elephant-goldfish's README has one pipeline
diagram, one "You have / Start with / Output" table, and one sequence diagram
per command.

**Recommendation.** Short term: add the "You have → start with → output" table
to `claude/README.md` and one mermaid pipeline diagram (the `.drawio` files in
`docs/diagrams/` do not render in GitHub). Medium term: decide on
`docs/consolidation-plan.md` — execute it or archive it; the longer it sits the
more the skill count grows around it.

#### R9 — Divergent lenses and a "what did they all miss" sweep in `/ideate`

**Observation.** `/design-twice` already runs parallel constrained agents for
interface shape; `/ideate` is a single-context interview. `eg-brainstorm` runs
3–5 lens agents (technical, business, UX, contrarian, prior art) in parallel
and then a contrarian sweep over the deduplicated set. The parallel step is
what produces divergence; the interview alone tends to converge on the first
framing.

**Recommendation.** Add an optional `--lenses` step to `/ideate` (after the
shared starting flow, before option analysis) that dispatches lens agents and
reports "what they agreed on / what they disagreed on". Add the contrarian
sweep to `/design-twice` step 4 as a fourth agent. Low cost; both skills are
`opus`-pinned and already interview-shaped.

#### R10 — Baseline-aware lint/typecheck in `/checkpoint`

**Observation.** `/checkpoint` notes that known pre-existing failures "should
be noted but not block", with no mechanism. `eg-precommit-review` diffs lint
output against a clean baseline so only *new* errors block. Prefer a
`git worktree add` of `default_branch` over its `git stash` script, which is
fragile.

**Recommendation.** Optional `--baseline` in `/checkpoint`: run lint/build in a
temporary worktree at `origin/<default_branch>`, diff the outputs, report
`new` vs `pre-existing`. Default off; `execute-plan` turns it on.

### 1.3 Repo hygiene noticed on the way (not elephant-goldfish related)

- `docs/` carries eleven planning/brief documents from completed or abandoned
  phases (`codex-port-plan`, `copilot-port-plan`, `kimi-port-plan`,
  `consolidation-plan`, three `gamma-*` briefs, two decks). Move completed
  ones to `docs/archive/`.
- `README.md` lines 37–43 use tab indentation inside the structure block and
  render unevenly.
- `claude/README.md` still says Kimi "auto-discovers `.claude/skills/`" while
  `manifest.json` installs a generated `kimi/skills` tree; one of them is
  stale.

### 1.4 What I deliberately did not recommend adopting

| elephant-goldfish feature | Why leave it out |
|---|---|
| Per-repo template rewriting (`[BOOTSTRAP: …]`) | Direct conflict with the single-source principle; it is exactly the "copied prompt sprawl" Philosophy.md rejects. The declared `## Commands` contract plus overlays gives the same stack awareness without forks. R6/R7 capture the useful part. |
| Fetch-over-`gh api` install with no local clone | This repo already has an installer with tests, orphan pruning, settings preservation and a CI gate. Lighter is not better here. |
| "Stop before commit" on every command | Governed autonomous execution commits per task on a run branch by design; `/pr` and `/ship` already show the message for approval. Different contract, not a gap. |
| Comprehension pass (Pass A) | Informational even in the source; `/simplify` and `/humanizer` cover prose clarity. |
| Gemini CLI adapter | No evidence of Gemini use in this repo beyond the `review-adversarial` fallback; a sixth platform tree is cost without a consumer. |
| Research goldfish with web search in PRD creation | `/prd-create` is interview-first and brownfield-seeded; `anthropic-skills:deep-research` and `WebSearch` exist natively. Cross-reference, do not rebuild. |
| Chrome MCP / simulator walkthrough steps | Host-specific; the built-in `/verify` already sits in `/checkpoint` step 6a and the runtime checkpoint. |
| Literal `no findings` / `lens complete` sentinels | The runtime uses JSON schemas; strictly better. |
| `eg-` namespace prefix | Collision avoidance for a five-command set; irrelevant at 50 skills with a plugin namespace coming. |

### 1.5 Suggested order

1. R4 (runtime defects already flagged twice) and R1 (blind review contract)
   together, since R4's re-review step wants R1's prompt rules.
2. R5 (interaction gates) and R6 (`/configure commands`) — onboarding and
   safety, no runtime risk.
3. R2, R3 — skill-level protocol additions.
4. R7, R8, R9, R10 — knowledge and ergonomics.


---

## Part 2 — Comparison with `docs/plans/elephant-goldfish-enhancements.md` and combined recommendation

### 2.1 Shape of the plan

The plan is a six-section enhancement brief with a four-phase roadmap. It is
not in the `_internal/plan-format` contract (no frontmatter, no `## Task N:`
sections, no `write_scope`, no mechanical acceptance bullets), so
`/validate-plan` would reject it and `/execute-plan` cannot run it. It *is* a
good requirements source: `/execute-prd docs/plans/elephant-goldfish-enhancements.md --type feature`
would compile it into an executable plan, which is the route recommended in
§ 2.4.

### 2.2 Side by side

Both analyses start from the same reading of elephant-goldfish (context
asymmetry as the lever) and reach the same top-level conclusion: infuse the
mechanisms into existing skills and `_internal` contracts, do not import
`eg-*` as competing skills. The differences are in where each looks and what
each leaves out.

| Theme | Plan | Part 1 | Agreement |
|---|---|---|---|
| Blind diagnosis in `/triage` | §1: hidden hypothesis, blind `Explore` agent, `Diagnosis Agreement` report field | R2, same shape | **Same.** |
| `/hotfix` | §1: failing test observed failing *before* fix; triviality gate | R2 (optional blind diagnosis), later deferred for hotfix | **Plan is better here.** Fail-first is cheap, already half-stated in hotfix ("Always add a test"), and does not add an agent dispatch. Adopt. |
| Cold-reader readiness | §2: comprehension paraphrase **and** "zero follow-up questions" passes in `/spec-review-adversarial` or `/prd-validate`; `--deep` in `/validate-plan` or `/kickoff` | R3: readiness lens in `/spec-review-adversarial`; `--cold-reader` in `/validate-plan`; comprehension excluded | **Agree on readiness, disagree on comprehension** (see § 2.5). Agree the plan-level pass belongs in `/validate-plan` so `/execute-prd` step 9 and `/kickoff` step 3 both get it. |
| Divergent lenses in `/ideate` | §3: `--divergent` mode, seed, 3–5 lenses, contrarian sweep | R9, deferred | **Same idea, different priority** (see § 2.5). |
| `/prd-create` research | §4: parallel Step 1 codebase grounding; optional `--research` wave | Not raised (parallel Step 1); excluded (research wave) | Adopt parallel Step 1. Leave the research wave out (see § 2.5). |
| Intent-free review | §5.1: `--cold` mode in `/domain-review`, or blind `correctness`/`security` workers; re-invocation addendum; same-location oscillation breaker | R1: `_internal/blind-review` contract consumed by `run-plan.mjs`, `/review-adversarial --blind`, `/domain-review` | **Complementary.** The plan's per-domain split (blind for correctness and security, intent-aware for architecture and requirements) is the right refinement of R1. The plan's gap is that it changes only `/domain-review` prose; the review that actually runs in a governed execution is dispatched by `run-plan.mjs`, which passes `Intent:` itself. |
| Rebuttal discipline | §5.2: four rebuttal categories into `_internal/disposition`; ban "I meant to do that"; verbatim surfacing | R4 (part): add "no silent dismissals" to disposition | **Same.** Plan is more specific; adopt its wording. |
| Baseline lint | §5.3: `git stash create` recipe plus a worktree alternative in `/checkpoint` | R10: worktree only, deferred | Partial. If adopted, worktree only: the stash recipe runs `git clean -fd`, which `claude/settings.template.json` denies, so it would fail in every repo installed by `skills --claude`. |
| Test-modification guard | §5.4: never silently rewrite a failing test | Not raised | **Plan is better.** Adopt, and put it in `run-plan.mjs` `implPrompt` as well as `/checkpoint`, since the runtime's implementer is where a silent test rewrite would actually happen. |
| Interactivity guard | §6.1: override clause in `_internal/aers-readiness` and the interview skills | R5: new `_internal/interaction-gates` contract | **Same rule, different home.** `aers-readiness` is a scoring rubric for requirements artifacts; an interaction rule does not belong there and would be missed by `/grill-me`, `/ideate` and `/goal`, which never read it. Use a dedicated contract. |
| Two-step scoped refinement | §6.2 | Not raised | **Plan is better.** Cheap, and it fixes a real UX problem ("what would you like to change?"). Fold into the interaction-gates contract. |
| Runtime defects | Not mentioned | R4: null review → `[]`; fixer self-closes findings; `allTasksImplemented` unread; `AUTO_ACCEPT` and adversarial trigger hard-coded against the documented contract | **Missing from the plan.** These were flagged High on 2026-09-04 and are the mechanism by which intent leaks and findings close without verification in every governed run. Writing a blind-review rule into prose while the runtime keeps passing `Intent:` changes nothing for `/execute-plan` users. |
| `/review-adversarial` | Named in §5 "current state", no recommendation | R1: `--blind` variant; degraded mode when no opposite-model CLI | Missing from the plan. |
| Onboarding (`## Commands` inference) | Not mentioned | R6: `/configure commands` with a stack profile | Missing from the plan. elephant-goldfish's bootstrap stack profile is its most user-visible feature; the plan skips it entirely. |
| Entry-point legibility | Not mentioned | R8 | Missing; low cost. |
| Stack overlays | Not mentioned | R7, deferred | Both defer. |
| Cross-platform sync | Phase 4: "propagate to `codex/`, `copilot/`, `kimi/`, `hermes/`" | Noted as a per-wave cost | The plan's verification list omits the CI set that actually guards parity: `bin/build-kimi-plugin --check`, `bin/validate-native-parity`, `bin/sync-native-contracts --check`, `python3 -m unittest discover -s tests`. Kimi regenerates from `claude/`; Codex and Copilot are manual ports. |

### 2.3 Assessment

The plan is a sound skill-prose plan and catches three things Part 1 missed
(fail-first in hotfix, the test-modification guard, two-step refinement). Its
weakness is that it treats `SKILL.md` prose as the whole system. In this repo
the review-fix loop, the reviewer prompt, the implementer prompt and the
verdict all live in `run-plan.mjs`, and that file has three open High findings
that the plan's own goals depend on. It also puts the interaction rule in the
wrong contract, omits onboarding, and includes two items (comprehension pass,
research wave) whose cost is not justified.

### 2.4 Combined recommendation

Compile the combined scope through this repo's own pipeline rather than
executing the brief by hand: treat a revised
`docs/plans/elephant-goldfish-enhancements.md` as the requirements source,
run `/execute-prd --type feature`, and let it produce a task-graph plan with
write scopes and mechanical acceptance. The waves below are the content that
revised brief should carry.

**Wave 1 — contracts and runtime (the foundation everything else cites).**

1. `claude/_internal/blind-review/SKILL.md` (new): what a blind reviewer
   receives and must not receive; exact-template rule; re-invocation
   addendum ("previous round's fixes — verify each; look for issues the fixes
   introduced"); same-location oscillation breaker (~10 lines); round cap.
2. `claude/_internal/interaction-gates/SKILL.md` (new): autonomous-mode
   detection; skill-enumerated gates are protocol, not clarifying questions;
   explicit same-turn opt-out phrase; one named non-negotiable gate per
   skill; the two-step scoped-refinement pattern. One paragraph each skill
   pastes verbatim.
3. `claude/_internal/disposition/SKILL.md`: the four rebuttal categories,
   the ban on unverifiable intent claims, verbatim surfacing in reports.
4. `run-plan.mjs`: null or failed review throws (as `checkpoint` already
   does); breakpoint review blind by default, `full` intent-aware; one blind
   re-review per gate closes findings instead of the fixer's self-report;
   `allTasksImplemented === false` → FAIL; read `auto_accept_deviations` and
   `adversarial_triggers` from the contract; align the adversarial fallback
   with `/review-adversarial`'s auto-mode rule; add the test-modification
   guard to `implPrompt`. Extend `tests/test_native_workflows.py` for
   missing-review and false-fixed cases.

**Wave 2 — review and bug-fix skills.**

5. `/domain-review`: `correctness` and `security` workers blind; others
   intent-aware; `pr_description` opt-in; cite the blind-review contract.
6. `/review-adversarial`: `--blind` variant and a blind-only degraded mode
   when no opposite-model CLI is available (instead of skipping).
7. `/triage`: hidden hypothesis, blind diagnosis agent, `Diagnosis Agreement`
   report line; skipped under `--quick`.
8. `/hotfix`: regression test observed failing for the expected reason before
   the fix; triviality gate for copy, config and version-bump changes. No
   mandatory diagnosis agent.
9. `/checkpoint`: test-modification guard; optional `--baseline` using a
   temporary worktree at `origin/<default_branch>` (no stash recipe).

**Wave 3 — requirements, planning and onboarding.**

10. `/validate-plan --cold-reader`: one fresh agent, plan file only, "list
    every question you would have to ask"; findings become `plan-ambiguity`
    and feed the existing 3-cycle fix loop. `/execute-prd` step 9 and
    `/kickoff` step 3 turn it on.
11. `/spec-review-adversarial`: fifth lens, **Readiness** (first-pass
    implementer, no follow-up questions).
12. `/prd-create`: parallel Step 1 (two `Explore` agents: existing surfaces,
    architecture and conventions). Add a one-line cross-reference to the
    native research skills instead of a research wave.
13. Interaction-gates block pasted into `/goal`, `/prd-create`,
    `/prd-validate`, `/ideate`, `/grill-me`, `/design-twice`, and the
    interactive/autonomous branches of `/execute-prd` step 4, `/execute-plan`
    gate 4, `/kickoff` step 2.
14. `/configure commands`: infer lint/build/test/package manager from
    manifests and `.github/workflows/*.yml`, print the stack profile, confirm,
    write `## Commands`; offer the deny list from `settings.template.json` to
    plugin users.
15. `claude/README.md`: "You have → start with → output" table and one
    mermaid pipeline diagram.

**Every wave ends with** `bin/build-kimi-plugin` (regenerate) and the full CI
set, plus manual ports of changed skills to `codex/` and `copilot/` with
`bin/validate-native-parity` green. Hermes carries only four skills; only
`validate-plan` and `execute-plan` changes reach it.

### 2.5 Left out of the combined program, with reasons

| Item | Proposed by | Reason for leaving it out |
|---|---|---|
| Comprehension paraphrase pass (Pass A) | Plan §2 | Informational even in elephant-goldfish ("comprehension is informational: log it, do not gate on it"; round 2+ skips it). It costs a dispatch per spec and produces no decision. `/simplify` and `/humanizer` already cover prose clarity, and the readiness pass subsumes the actionable part: a doc a cold implementer cannot paraphrase is one they will have questions about. |
| External research wave in `/prd-create` (`--research`) | Plan §4 | `docs/Philosophy.md` § "Built-ins first": `anthropic-skills:deep-research` and `WebSearch` already exist in the host. `/prd-create` is interview-first and brownfield-seeded by design; a research wave with 3–5 web-searching agents is the most expensive step in elephant-goldfish and the one its README warns about. Cross-reference, do not rebuild. |
| `--divergent` lenses in `/ideate`, contrarian sweep in `/design-twice` | Plan §3, Part 1 R9 | `/ideate` already defers to `superpowers:brainstorming` for the design step. Adding parallel lens agents to an interview skill multiplies token cost with no observed convergence problem to fix. Keep as a candidate for a later wave once Waves 1–3 show whether blind agents are being used. |
| `git stash create` baseline recipe | Plan §5.3 | Runs `git checkout -- :/ && git clean -fd`; `git clean -f*` is on the deny list this repo installs. It would be blocked in every `skills --claude` repo and is destructive-adjacent where it is not. The worktree form is kept, as optional. |
| Interactivity clause in `_internal/aers-readiness` | Plan §6.1, Phase 1 | Wrong home. `aers-readiness` is read only by `execute-prd`, `kickoff` and `prd-validate` to score artifacts; `/goal`, `/ideate` and `/grill-me` never load it, so the clause would not reach the skills that most need it. Replaced by a dedicated contract. |
| Blind diagnosis agent in `/hotfix` | Part 1 R2 | `/hotfix` is "speed over ceremony" by contract. The plan's fail-first test gives most of the anchoring protection at zero dispatch cost. Reconsider after `/triage` shows whether the agreement line changes decisions. |
| Stack overlays and `layer_order` | Part 1 R7 | Pure content with no gating effect; add when a consuming repo on that stack exists. |
| Executing `docs/consolidation-plan.md` | Part 1 R8 (medium term) | A separate product decision with its own plan. Decide to schedule or archive; do not bundle. |
| Plan Phase 4 as written ("propagate to all platforms") | Plan | Not dropped, but replaced by the per-wave CI gate above. A single trailing "propagate" phase with no parity check is how the 2026-09-04 review found Codex and Copilot behind Claude. |
| Per-repo template rewriting, `gh api` fetch install, stop-before-commit on every command, Gemini adapter, Chrome MCP steps, literal sentinels, `eg-` prefix | elephant-goldfish | Rejected in Part 1 § 1.4; nothing in the plan changes those reasons. |

### 2.6 Why this order

Wave 1 first because every later item cites one of its contracts, and because
the runtime defects are already two reviews old and reach every governed run.
Wave 2 before Wave 3 because review and bug-fix changes are where the blind
pattern pays off immediately; requirements and onboarding changes are
quality-of-life. Items 10 and 11 could move up if `/execute-prd` runs are
hitting gate-4 ambiguities often; nothing in the data in this repo says they
are.

---

## Appendix — Side comparison with `docs/plans/2026-09-10-claude-plugin.md`

Read first by mistake (no file named `implementation_plan.md` existed at the
time). It is a distribution plan, orthogonal in content to everything above,
and ready to run as written. Two notes worth keeping:

- **Unverified cross-skill resolution under the plugin namespace.** Task 2
  counts skills loaded as `savviety-workflows:<name>` but nothing exercises
  one skill invoking another. Every orchestrator here calls siblings by bare
  `/name` (`/execute-prd` → `/validate-plan`, `/execute-plan`,
  `/audit-existing`; `/pr` → `/checkpoint`). Add one headless
  chained-invocation check to Task 2 or Task 6 before relying on the plugin.
- **Interaction with this review.** The plugin ships `run-plan.mjs` as-is, so
  Wave 1 item 4 should land in the same release. The plugin cannot ship the
  permissions deny list; Wave 3 item 14 (`/configure commands`) is the natural
  place to offer it to plugin users, replacing the plan's README caveat with an
  action.
