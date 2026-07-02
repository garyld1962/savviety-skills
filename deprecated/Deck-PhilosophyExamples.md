# Flagship Skills — The Philosophy in Practice

Four real skills from `claude/` that embody the deck's loop —
**Goals reduce guessing · Context reduces noise · Constraints reduce wandering ·
Validation reduces retries**. Quotes are verbatim with `file:line` so they're citable
on a slide.

Ordering: one skill that runs the *whole* loop, then three that each own one principle.

---

## 1. `execute-plan` — the whole loop in one skill ⭐ (hero example)

*What it is:* runs a written plan end-to-end with staged reviews. If you show one slide,
show this one — all four principles operate at once.

| Principle | How this skill does it | Cite |
|---|---|---|
| **Goal** | Named job + refuses work outside it: refuses to run on the default branch; refuses to execute if the plan fails its gate | `execute-plan/SKILL.md:111, 217` |
| **Context** | "parallel waves with single-message dispatch in **isolated git worktrees**"; hands `code-review` a pre-computed `diff_manifest` so it skips re-triage | `:26, :31` (code-review) |
| **Constraint** | **Retry budget circuit breaker** — `max_total_retries: 20 / max_wall_clock_minutes: 60` | `:294, :306–310` |
| **Validation** | `validate-plan` → per-task build/test → breakpoint review per milestone → full + craft + adversarial review | `:9–11` |

**The one-liner that *is* the philosophy:**
> "On impasse — retry-budget exhaustion or a task that loops without converging … cheap
> retries on a wrong mental model just **burn budget**." — `execute-plan/SKILL.md:26`

---

## 2. `code-review` — Context, engineered (not dumped)

*What it is:* a coordinator that fans a change out to domain specialists. Best illustration
of "the smallest useful packet."

- **Scope, not dump:** "Only the files the domain needs … **Do not dump the whole repo.**"
  — `code-review/SKILL.md:124`
- **Reuse, not re-triage:** if a `diff_manifest` is supplied, "**skip step 2 (Triage the
  diff)** — the manifest already supplies the clusters." — `:31`
- **Spend tokens only where they apply:** "Conditional domains **fire only when triggers
  match**" (e.g. data-integrity fires only if the diff touches persistence). — `:8`
- **Coordinator owns its lane:** "You are the coordinator … **You do not review code
  yourself.**" — `:20`

> Token point: this is *Context reduces noise* made literal — selected, shaped, reused.

---

## 3. `parallel-optimization` — Constraints, declared up front

*What it is:* turns a plan into safe parallel lanes. Best illustration of "boundaries are
cheaper when declared."

- **Disjoint write scopes:** "Lanes have **disjoint write scopes**, or the overlap is
  explicitly [owned]." — `parallel-optimization/SKILL.md:78`
- **Narrow packet per lane:** each lane gets a "**Shared Context Packet**," not the full
  history. — `:158`
- **Barriers, not constant waiting:** "Use **milestone barriers** instead of waiting after
  every task." — `:136`
- **Refuses unsafe scale** (cited in `execute-plan`): "Refuse ≥5 parallel teams in a single
  wave."

> Token point: *Constraints reduce wandering* — the model never discovers a boundary by
> crashing into it.

---

## 4. `validate-plan` — Validation that prevents the retry loop

*What it is:* a cheap gate run *before* execution. Best illustration of "a clear check beats
five rounds of try-again."

- **Mechanical, not vibes:** "Every task must declare acceptance in a form that can be
  **checked mechanically — not interpretive prose.**" — `validate-plan/SKILL.md:52`
- **Batch the failures:** "**report all failures at once** so the author can fix them in one
  pass." — `:25`
- **No hand-waving:** rejects `TBD`, `TODO`, `[placeholder]` with line numbers. — `:108–115`

> Token point: *Validation reduces retries* — a few cheap tokens up front kill an expensive
> downstream loop. This gate is *why* `execute-plan` rarely burns its retry budget.

---

## How they chain (optional closing slide)

These aren't four isolated skills — they're one pipeline, each enforcing its principle:

```
validate-plan      →     execute-plan      →      code-review
(Validation gate)     (Constraints + the      (Context, fanned out
                       whole loop)             to scoped specialists)
        ↑
parallel-optimization defines the lanes execute-plan runs
```

> The loop isn't a diagram on a slide. It's wired into the skills that ship the code.

---

# The Philosophy, Caught in the Act (live run evidence)

The four skills above are the *design*. These three moments are the *proof they ran* — pulled
verbatim from a real `/execute-plan` session
(`runs/2026-06-07-skill-adapter-5a/session-transcript.jsonl`, cited as `:line`). Use these
when someone says "fine, but does it actually do that?"

---

## Evidence 1 — Context + Constraint: it reviews the lenses that apply, skips the ones that don't

Right before the parallel review, the model writes out its domain selection and **drops two
domains with stated reasons** (`:301`):

```
## Selected domains
- concept/security        [always]
- concept/data-integrity  [conditional: SQLite migration in db.ts]
- concept/api-contract    [skipped: no public surface / message-schema change]
- platform/postgres       [skipped: better-sqlite3, not postgres]

Dispatching the 10 domain workers in parallel (tiny diff, behavior-preserving…)
```

> **Context reduces noise + Constraints reduce wandering.** Zero tokens spent reviewing API
> contracts or Postgres — it can see neither applies, and says so before spending anything.

---

## Evidence 2 — Validation: a mechanical check catches what the tests missed

A review fix made **all 420 tests pass** — but the plan's acceptance grep caught a regression
the tests waved through (`:354`):

```
Tests  420 passed (420)
=== M1 acceptance grep still clean? ===
skill-registry.ts:350: const isExtension = (s) => s.source === 'extension' || s.owner === 'extension';   FAIL
```

The model reasons it out and **reverts** rather than ship green-but-wrong (`:357`):

> "The `isExtension` fix reintroduces `owner === 'extension'` … which **trips the plan's
> explicit acceptance criterion** … I'm reverting that fix."

Then re-runs the gate (`:366`):

```
Tests  419 passed (419)
=== acceptance grep (must be clean) ===   PASS: clean
```

> **Validation reduces retries.** "Tests pass" wasn't proof — a declared, mechanical check
> was. "A clear check beats five rounds of try-again," happening live.

---

## Evidence 3 — Goal + Constraint: it hits a call it shouldn't make alone, and stops instead of guessing

The adversarial pass found a pre-existing security gap. The model neither silently fixes it
nor silently ignores it — it **surfaces the decision** with scoped options (`:456`), then
files **BAK-266** once told (`:467, :470`):

> "Adversarial review surfaced a PRE-EXISTING authz gap … How do you want to handle it?"
> - **Ship 5a, file follow-up** — "Keep it scope-disciplined … **Don't expand 5a.**"
> - **Harden self-management now** — "Behavior-changing, out of the plan's stated scope."
> - **Let me see the code first.**

> **Goals keep it in its lane** (it owns 5a and refuses to scope-creep into a fix that isn't
> its job) **+ the impasse is surfaced, not guessed** — it stops and asks rather than burning
> tokens on a security call it shouldn't make alone.

---

> Design on the left, proof on the right: the skills declare the loop, and the transcript
> shows it running.
