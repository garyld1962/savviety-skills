# Token Economy: Global CLAUDE.md → Skills

How the global behavioral contract establishes token economy as a first-class
constraint, and how individual skills implement it with concrete, distinct
mechanisms. Line numbers are exact and citable.

---

## Part 1 — The global contract (`~/.claude/CLAUDE.md`)

Token economy is not an aside in the global instructions; it is **Section 2 of
10**, placed immediately after "Think before coding." It governs three separate
budgets — what you **read**, what you **write**, and what you **reuse** — and
returns again in Section 10 as context-window hygiene.

### § 2. Token efficiency — the three budgets

| Line | Instruction | What it saves |
|---|---|---|
| 37 | "Don't dump, don't narrate, don't re-emit." | The one-line thesis; names all three waste modes. |
| 40 | "Targeted reads over broad exploration. `rg` plus `view` with line ranges, not `cat` on whole files." | **Input** — never pull a whole file when a range answers the question. |
| 41 | "Don't re-read files already in context this session." | **Input** — eliminates duplicate reads of cached content. |
| 42 | "Don't enumerate a directory tree when you need one file." | **Input** — no `ls -R` to fetch a single path. |
| 43 | "Sample, don't exhaust — 20 lines of a log usually tell you what 20,000 would." | **Input** — bounded sampling over exhaustive reads. |
| 44 | "Prefer `--help`, `man`, or a focused grep over reading a whole doc." | **Input** — answer specific questions without ingesting the doc. |
| 47–49 | "No preamble… No recap… Don't narrate routine actions." | **Output** — kills filler tokens around every action. |
| 52–53 | "Prose over bullets when continuous. Match reply length to question weight." | **Output** — structure and length scale to the question. |
| 56 | "Don't re-emit unchanged code. Use `str_replace` and targeted edits, not full-file rewrites." | **Reuse** — edit diffs, never re-print the file. |
| 57–58 | "Don't repeat the same caveat… Don't restate the plan after executing it." | **Reuse** — no echoing context the user already holds. |
| 59 | "When summarizing prior work, compress aggressively — the user already lived through it." | **Reuse** — recap is compression, not replay. |
| 61 | "Test: if removing a sentence wouldn't change what the user can act on, remove it." | The falsifiable acceptance test for every token spent. |

### § 10. Context-window hygiene — clearing the largest budget

| Line | Instruction | What it saves |
|---|---|---|
| 145–147 | "Suggest clearing context at natural phase boundaries… prior context becomes ballast." | Frees the whole window when accumulated context stops paying rent. |
| 151 | "Review → fix. Start a fresh session to fix findings." | Drops reviewer-framing context before implementation. |
| 152 | "Long debugging → clean attempt. After 15+ turns… context is polluted with wrong hypotheses." | Sheds dead hypotheses that bias and bloat. |
| 153 | "Multi-repo work. The prior repo's file contents waste context." | Releases stale file reads on repo switch. |
| 159–164 | "Mid-session context drift… most of the existing context is dead weight." | Flags divergence so the user can reset to a 2–3 sentence task. |

**Through-line:** the global file frames tokens as a *budget with a test* (line
61), not a vibe. Every skill below is an application of one of these rules.

---

## Part 2 — Skills with distinct token-saving mechanisms

Seven skills, each illustrating a **different** technique. Paths are relative to
`claude/`.

---

### 1. `code-investigate/SKILL.md` — return pointers, not payloads

The canonical implementation of global line 40 ("line ranges, not whole files").
A fan-out search skill that returns structured **`file` + `lineRange`** matches
by default and makes the expensive payloads *opt-in*.

| Line | Example | Savings |
|---|---|---|
| 39 | `--include-code` — matching code lines are **opt-in**, off by default | Report ships locations, not source; code only when explicitly asked. |
| 40 | `--include-summary` — per-match behavior summary is **opt-in** | No generated prose per hit unless requested. |
| 84–85 | Required match fields are `file` + `lineRange` (`e.g. 42-58`) | A hit is a clickable pointer, not an excerpt. |
| 90–91 | `codeLines` / `summary` columns are "no" (optional) — "Only when `--include-code` / `--include-summary`" | Schema enforces the opt-in: heavy fields are structurally absent by default. |

**Technique:** *pointer-by-default, payload-on-demand.*

---

### 2. `execute-plan/SKILL.md` — isolate context, summarize across the boundary

Long-running orchestrator. Its token discipline is **architectural**: work is
pushed into subagents/worktrees so their context never lands in the main window,
and only summaries cross back.

| Line | Example | Savings |
|---|---|---|
| 279–280 | Decision-record body "is a pointer, not a specification — the canonical doc wins." | Inlines a reference, not the full rubric (global §2 reuse). |
| 736–737 | Parallel lanes run in "isolated git worktrees with a fresh subagent per lane." | Each lane's file reads/edits stay out of the main context entirely. |
| 899 | Per-task return is `Task N/M: DONE — <brief summary>`. | Subagent returns one line across the boundary, not its transcript. |
| 1014 | Resume state is "a one-line summary of completed tasks." | Reconstructs progress from a pointer, not a replay. |
| 1708 | Postmortem is "**Not a chat-transcript summary.** No turn-by-turn replay." | Explicitly forbids the most expensive output anti-pattern. |
| 294–352 | Retry/wall-clock **budget circuit breaker** (default 20 retries / 60 min) | Caps doomed retry loops — the compute analogue of a token budget. |

**Technique:** *context isolation + summary-only boundaries + hard budgets.*

---

### 3. `checkpoint/SKILL.md` — scope work to the diff, not the repo

Implements global line 40 at the level of *which work runs at all*: lint, build,
and tests execute only for **changed packages**, never the whole tree.

| Line | Example | Savings |
|---|---|---|
| 8 | "Runs lint, build, and tests **for changed packages**." | Bounds the entire gate to the diff. |
| 46 | "Step 2: Identify Changed Packages" | Derives scope from changed files first. |
| 66 | Maps changed file paths → workspace package names | Only affected packages enter the run. |
| 106–108 | "Run Tests **for Changed Packages**… For each changed package identified in Step 2" | Test execution (and its output) is diff-scoped. |

**Technique:** *diff-scoped execution* — don't process what didn't change.

---

### 4. `code-review-professional/SKILL.md` — compute silently, emit only the verdict

A reviewer that runs a self-audit pass but is explicitly told **not to print it**
— a direct application of global line 49 ("don't narrate") and line 61 ("if it
doesn't change what the user can act on, remove it").

| Line | Example | Savings |
|---|---|---|
| 211 | "Run silently — **do not include the audit in the output**. Use it to revise the report." | The reasoning pass costs zero output tokens. |
| 211 | "If a finding cannot be revised to pass the audit, **drop it**." | Weak findings are deleted, not hedged into the report. |
| 134 | Component summary capped at "a short paragraph (3–5 sentences)." | Output length is bounded by contract. |

**Technique:** *silent intermediate reasoning* — think wide, emit narrow.

---

### 5. `work-item/SKILL.md` — distill the source, don't relay it

Fetches tracker tickets (ADO/Linear) and returns clean markdown instead of the
raw API response — global §2 input + output economy at the integration edge.

| Line | Example | Savings |
|---|---|---|
| 14 | "You want a **clean markdown summary rather than raw API JSON**." | Strips verbose API envelopes; only title/description/criteria survive. |

**Technique:** *distill-at-ingress* — never let raw upstream payloads into context.

---

### 6. `changelog/SKILL.md` — shape the command output at the source

Rather than reading full `git log` output and trimming it afterward, it formats
and filters **in the command** so only the needed bytes ever arrive (global line
44, "focused" tooling).

| Line | Example | Savings |
|---|---|---|
| 55 | `git log … --pretty=format:"%H %s" --no-merges` | Returns just hash + subject; drops author/date/body and merge noise. |

**Technique:** *format-at-source* — push projection into the tool, not the model.

---

### 7. `repo-status/SKILL.md` — prefer the compact form of every command

A status snapshot built entirely from the short/summary variants of git
commands, so the report is dense by construction.

| Line | Example | Savings |
|---|---|---|
| 27 | Default invocation is "current repo, **summary form**." | Compact output is the default, not an option. |
| 46 | `git status --short` — "modified/untracked summary." | Short status over the verbose multi-line default. |
| 47 | `git stash list` — "count + first line of each." | Bounded per-item output, not full stash diffs. |

**Technique:** *compact-by-default* — choose the terse variant of every probe.

---

## Synthesis: each skill maps to a global rule

| Global rule (CLAUDE.md line) | Implementing skill | Mechanism |
|---|---|---|
| 40 — line ranges, not whole files | `code-investigate` (39–91) | Pointer-by-default, payload opt-in |
| 41/153 — don't re-read; isolate context | `execute-plan` (736, 899, 1708) | Subagent/worktree isolation + summary boundary |
| 40 — targeted over broad | `checkpoint` (8, 106) | Diff-scoped execution |
| 49/61 — don't narrate; remove the inert | `code-review-professional` (211) | Silent audit; drop weak findings |
| 39/59 — distill, don't dump | `work-item` (14) | Distill-at-ingress |
| 44 — focused tooling | `changelog` (55) | Format-at-source |
| 43/53 — sample; match output to weight | `repo-status` (27, 46) | Compact-by-default |

The global file sets the budget and the test (line 61); the skills are seven
distinct strategies for staying under it — at the read, the run, the reasoning,
the ingress, and the command level.
