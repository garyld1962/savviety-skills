# Token Management — Real-Run Evidence

Concrete examples of the ten token-management strategies (from `TopTenTokenManagement.md` /
the Gamma deck), mined from a real `/execute-plan` run.

**Source run:** `runs/2026-06-07-skill-adapter-5a/session-transcript.jsonl`
(Baker Street item-5a — behavior-preserving SQLite migration making `source` the sole
runtime-extension discriminator). Citations are `L<n>` = line number in that JSONL.

**How to read this:**
- **Hard** = a literal, quantifiable artifact in the transcript (token counts, parallel
  dispatch, line-range reads). Demo-quotable with a number.
- **Soft** = the pattern is present/implemented but not a dramatic metric.
- **Rating** = `STRONG` (great demo material) · `WEAK` (present but thin) ·
  `NOT-IN-RUN` (needs a different example — flagged honestly so we don't overclaim).

---

## Run-level facts (the numbers behind everything below)

| Metric | Value | Source |
|---|---|---|
| JSONL events | 521 | file |
| Assistant turns | 235 | all `claude-opus-4-8` (main thread) |
| Context window: min → peak | **73,543 → 297,384 tokens** | usage on assistant turns |
| Total main-thread output | **389,502 tokens** | sum of `output_tokens` |
| Subagent (`Agent`) dispatches | **13** | across 4 review phases |
| Tool calls | Bash 45 · Read 18 · Edit 18 · Write 6 · Skill 5 | tool_use scan |
| Human-in-loop gates | **2** (`AskUserQuestion`) | L30, L456 |
| Platform | **Irene / macOS** (`/Users/gary/...`) | — not WSL, so no RTK |

**Workflow spine (the 5 skills):**
`validate-plan` (L49) → `code-review` profile:breakpoint (L132) →
`code-review` profile:full (L290) → `code-review-professional` (L381) →
`review-adversarial` (L390).

> ⭐ **The single best demo moment** is the **8-domain parallel review** (L302–309). It
> demonstrates *four* strategies at once — see [#3b](#3b), [#5a](#5a), [#1a](#1a), and the
> scope-gating in [#5a](#5a). This is the "8 domain parallel run" you flagged.

---

## Group 1 — Context Budget Management

### 1a. Three-Axis Token Budget {#1a}

**Rating: STRONG (input axis) · WEAK (output/context axes)**

- **Hard — input axis (targeted reads, never whole files):** the domain-worker prompts
  instruct line-range reads, not file dumps:
  > "Read your concept prompt … `data-integrity.md` … `db.ts` (migration block; **also
  > rowToMetadata ~line 800-825** … `db.ts` (read **~line 170-213**)" — L302.

  Main-thread Bash is uniformly piped/bounded: `… | head -20`, `… | tail -15`,
  `… | tail -8`, `… | head -5`, `rg -n -w 'TBD|TODO|…'` (45 Bash calls, all terse). No
  `cat` on a whole file appears.
- **Soft — context axis:** edits are surgical (18 `Edit` vs only 6 `Write`) — changed code
  is patched, not re-emitted.
- **Demo line:** *"Every file read in this run is a line-range or a piped tail — the agent
  reads `db.ts:170-213`, not `db.ts`."*

### 1b. Context Window Phase Clearing {#1b}

**Rating: STRONG (as subagent isolation) · NOT-IN-RUN (as literal `/clear`)**

This run never calls `/clear` (it's one continuous session). But it achieves the *same goal*
structurally: each review phase runs in **isolated subagent windows** so the exploration
cost never lands in the main thread.

- **Hard:** at the 8-domain dispatch the main thread held **192,276 tokens** (L301). The 8
  workers each then did deep multi-file reads **in their own windows**; when they returned,
  the main thread rose only to **230,503** (L356) — **+38k for 8 deep reviews**. Inline,
  those 8 read-heavy passes would have blown past the window.
- **Demo line:** *"Phase isolation without `/clear`: 8 reviewers read deeply, the parent
  context grew 38k, not 8×."*

### 1c. Cross-Session Memory Compression {#1c}

**Rating: NOT-IN-RUN (no `.remember`/ccx digest in transcript) · SOFT (artifacts produced)**

No memory-digest read appears in this session. The *outputs* of the run are themselves the
compression layer for future sessions: `execution-report.md`, `postmortem.md`, and the
rendered `session-transcript.md` — a fresh session reads those instead of replaying 521
events. If we want a hard memory example, pull it from a Sherlock/WSL session that opens
with a `ccx_digest()` / `.remember/now.md` read.

---

## Group 2 — Cost-by-Capability Routing

### 2a. Model Tier Pinning {#2a}

**Rating: STRONG (cross-model routing) · NOT-IN-RUN (multi-tier within Claude)**

Main thread is 100% `claude-opus-4-8`, so there's no haiku/opus split to show. **But** the
adversarial phase deliberately routes to a *different model family*:
> "Phase 3e — adversarial. Step 0 preflight on **codex** (the hard constraint: reviewers
> run via the **opposite-model CLI, not subagents**)" — L395.
> `which codex && codex --version` → `codex-cli 0.136.0` — L396–397.

That's cost-by-capability *and* diversity routing: the three adversarial reviewers
(Skeptic / Architect / Minimalist) run on the opposite model so they don't share the
author's blind spots.

- **Demo line:** *"Routing isn't just cheap-vs-expensive — the adversarial pass runs on the
  opposite model on purpose, so the reviewer can't inherit the author's blind spots."*

### 2b. Haiku-as-Router {#2b}

**Rating: NOT-IN-RUN.** No Haiku dispatch is visible in this transcript. Needs a different
example (a dispatcher/lookup skill invocation showing the haiku pin).

---

## Group 3 — Tooling & Infrastructure

### 3a. RTK — Rust Token Killer {#3a}

**Rating: NOT-IN-RUN.** 0 of 45 Bash commands use `rtk` — this run was on Irene (macOS),
where RTK isn't installed. For a hard RTK example, capture a Sherlock/WSL session and show
`rtk gain` savings. (Flag this on the slide so it's not misattributed to this run.)

### 3b. Parallel Execution Lanes {#3b}

**Rating: STRONG — this is the headline example.**

- **Hard — 8 lanes, one turn, isolated packets:** at L302–309 a *single* assistant message
  (`id …R12hTy`) emits **8 `Agent` tool_use blocks**; all 8 `tool_result`s return together
  at L313–320. Each worker gets a **narrow self-contained packet** (its lens prompt + the
  specific files and line ranges) — *not* the conversation history. The dispatch prose:
  > "Dispatching the 10 domain workers in parallel (tiny diff, behavior-preserving …)" — L301.
- **Hard — also at the breakpoint:** 3 lanes dispatched together (Security / Correctness /
  Tests, `id …rXqZsg`) at L155–158.
- **Soft — the harness design:** `/execute-plan` is specified for "parallel waves with
  **single-message dispatch in isolated git worktrees**" (skill spec, L10).
- **Demo line:** *"One turn fans out to 8 review agents, each with its own context window
  and its own narrow packet. The parent doesn't carry 8 conversations."*

### 3c. WSL/Bash over PowerShell {#3c}

**Rating: SOFT (Unix-bash terseness shown, but on macOS not WSL).** The terse-output
principle is demonstrated — every command pipes through `head`/`tail`/`rg -n` and emits
compact text. But this is macOS bash, not WSL, and there's no PowerShell contrast in-run.
Use it to illustrate the *principle*; don't claim it as a WSL-vs-PowerShell measurement.

---

## Group 4 — Guardrails Against Runaway Spending

### 4a. Token Guardrail in Scanning (30% stop) {#4a}

**Rating: NOT-IN-RUN (no explicit 30% trip) · SOFT (achieved by targeted reads).** No
scanning skill hits the ~30% hard stop here (0 occurrences of the guard firing). The same
outcome is reached structurally: domain workers read line ranges, not whole trees, so no
single pass crowds out synthesis. For a hard 30%-guardrail example, use a
`security-quick-check`/`modernization-rubric` run on a large codebase.

### 4b. Retry Budget Circuit Breaker {#4b}

**Rating: STRONG (config present + breaker observed not tripping) · plus impasse-surfacing.**

- **Hard — the breaker config is live:** `/execute-plan` carries
  `retry_budget: max_total_retries: 20 / max_wall_clock_minutes: 60` (L10).
- **Hard — it held:** execution-report records "**~4 auto-fix cycles … within budget; no
  budget pressure**" — the circuit breaker was active and *not* tripped, which is the point.
- **Hard — impasse surfaced, not looped:** the adversarial pass found a pre-existing authz
  gap; instead of auto-fixing or looping, the run **stopped and asked the operator** (L456,
  see Group 5 / [#5a](#5a)) and **filed Linear BAK-266** (L467). That's CLAUDE.md §6
  ("surface the impasse") enforced as a guardrail.
- **Demo line:** *"The retry budget (20/60) is a circuit breaker. This run never hit it —
  4 fix cycles, no pressure — and when it found a security decision it couldn't make, it
  surfaced it to a human instead of looping."*

---

## Group 5 — Review Quality vs. Token Tradeoff

### 5a. Separate-Pass Domain Reviews {#5a}

**Rating: STRONG — richest, most multi-point example in the run.**

- **Hard — isolation forces depth:** 8 domain workers, each pinned to ONE lens, each its own
  context window (L302–309). Lenses dispatched: data-integrity, correctness+types,
  architecture, operability, security, tests, resilience+concurrency, performance+
  requirements — **10 review lenses across 8 parallel agents**.
- **Hard — scope-gating / least privilege:** **2 of 10 domains skipped by relevance**:
  > "concept/api-contract **[skipped: no public surface / message-schema change]** …
  > platform/postgres **[skipped: better-sqlite3, not postgres]**" — L301.

  Tokens aren't spent on lenses that can't apply to this diff.
- **Hard — layered review *types*, each its own pass:**
  breakpoint (3 domains, L155–158) → full (8 domains, L302–309) →
  professional craft-grade (L381/389) → adversarial cross-model (L390/395).
- **Hard — human gate on the one finding a model shouldn't decide:** L456 surfaces the
  blue-green authz gap with three operator options ("Ship + file follow-up" / "Harden now" /
  "Show me the code"); resolution → BAK-266 (L467).
- **Why it's the best slide:** this one moment shows **isolated domain depth (#5a) +
  parallel lanes (#3b) + targeted context packets (#1a) + scope-gating/least-privilege**
  simultaneously — the "several points at once" you noticed.
- **Demo line:** *"10 lenses, 8 isolated passes, 2 skipped because they can't apply. More
  total tokens than one combined prompt — but every token buys depth in exactly one domain."*

---

## Quick-pick matrix (for choosing slides)

| # | Strategy | Best example | Rating | Hard #? |
|---|---|---|---|---|
| 1a | Three-axis budget | line-range reads `db.ts:170-213` (L302) | STRONG | yes |
| 1b | Phase clearing | +38k for 8 deep reviews via isolation (L301→356) | STRONG | yes |
| 1c | Memory compression | report/postmortem as digest artifacts | NOT-IN-RUN | no |
| 2a | Model tier routing | adversarial runs on **opposite-model codex** (L395) | STRONG | yes |
| 2b | Haiku-as-router | — | NOT-IN-RUN | no |
| 3a | RTK | 0/45 bash (macOS run) | NOT-IN-RUN | no |
| 3b | Parallel lanes | **8 agents, one turn** (L302–320) | STRONG | yes |
| 3c | Bash terseness | head/tail/rg piping everywhere | SOFT | partial |
| 4a | 30% scan guardrail | targeted reads avoid full scans | NOT-IN-RUN | no |
| 4b | Retry circuit breaker | 20/60 config; 4 cycles, no trip (L10 + report) | STRONG | yes |
| 5a | Separate-pass reviews | **10 lenses / 8 passes / 2 skipped** (L302–309) | STRONG | yes |

**Strongest for the demo (have hard numbers):** 3b, 5a, 1b, 2a, 4b, 1a.
**Flag-as-not-this-run (use other footage or label clearly):** 1c, 2b, 3a, 4a.
