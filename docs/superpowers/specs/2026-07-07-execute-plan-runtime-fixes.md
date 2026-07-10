# execute-plan Runtime Fixes — Requirements Spec

**Date:** 2026-07-07
**Status:** Ready for execute-prd
**Author:** Gary + Claude (from a live end-to-end test in `~/repos/kb`)

## Execution notes — read before running anything

- **Run via `/execute-prd` in autonomous mode: proceed to completion
  without pausing for interactive gap-filling.** This document is
  written to be readiness-complete (exact file/line locations, exact
  fix shapes, exact acceptance commands) specifically so the AERS
  readiness gate scores it Ready (0–2 pts) and execute-prd never needs
  to stop and ask. If it does stop to ask something, that itself is a
  signal this doc has a real gap — fix the doc, don't paper over it by
  guessing.
- **Bootstrapping constraint — Requirement 0 must be applied manually,
  *before* invoking execute-prd, not as a task inside the generated
  plan.** `claude-new/execute-plan/workflows/run-plan.mjs` cannot
  complete *any* task right now — not even a trivial one — because of
  the two crash bugs below. Task 1 of any plan this runtime executes
  calls `implPrompt()`, which unconditionally dereferences
  `args.commands.build`; if that throws, nothing can run, including a
  plan whose Task 1 is "fix the thing that's throwing." Requirement 0
  is therefore a precondition, not a deliverable — apply it directly
  (see exact diff below), verify with `node --check`, commit it, and
  only then run `/execute-prd` for Requirements 1–3.
- **This repo's own `.claude/skills/` has been overlaid** with
  `claude-new/execute-plan`, `claude-new/execute-prd`,
  `claude-new/_internal`, and the fixed `claude/validate-plan`, plus a
  `.claude/settings.json` from `claude-new/settings.template.json` and
  a root `CLAUDE.md ## Commands` section — all done in this session, all
  uncommitted. Review and commit them (or adjust) before running
  anything; without them `/execute-prd`/`/execute-plan` are not
  invocable in this repo at all (no execute-* skill was self-hosted
  here previously), and without the `CLAUDE.md ## Commands` section,
  execute-plan's own gate 1 halts immediately.
- Evidence for all four findings below comes from the first-ever full
  end-to-end run of this runtime, executing a real 11-task plan
  (`~/repos/kb`, plan `docs/plans/2026-07-07-kb-v1-capture-search.md`,
  postmortem at `docs/runs/2026-07-07-212238/postmortem.md` in that
  repo). This was also the first time `claude-new/execute-plan/tests/smoke.md`
  would have been exercised in earnest — per `claude-new/HANDOFF.md` it
  had never been run. Requirement 3 below is that smoke test, finally.

## Problem

`claude-new/execute-plan/workflows/run-plan.mjs` (the Workflow-tool
runtime backing `/execute-plan`, staged in this branch for promotion
into `manifest.json`) has never completed a full end-to-end run. Its
first real test surfaced two crash bugs that block it from finishing
any plan at all, and two architectural gaps that let real critical
bugs ship silently under a passing-looking verdict. All four are
reproduced and confirmed against the actual file in this repo, not
just theorized.

## Requirement 0 (bootstrap — apply manually, not via execute-plan)

**0a. `args` may arrive as a JSON-encoded string instead of a parsed
object.** Confirmed via a throwaway diagnostic Workflow script in the
`kb` session: `typeof args === "string"` and every `args.foo` read was
`undefined`, even though the tool call passed a well-formed JSON
object as the `args` parameter. Root cause unconfirmed — could be this
specific `Workflow` tool call convention rather than a `run-plan.mjs`
bug per se — but the fix below is defensive either way and costs
nothing when `args` already arrives as a proper object.

**Fix:** immediately after the `meta` export (before the `// ----------
schemas ----------` comment, i.e. before line 12), insert:

```js
const cfg = typeof args === 'string' ? JSON.parse(args) : args
```

Then replace every remaining `args.` reference in the file with
`cfg.` (30 occurrences as of this writing — confirm count with
`grep -c 'args\.' claude-new/execute-plan/workflows/run-plan.mjs`
before and `grep -c 'cfg\.' ...` after; they should match). Do not
rename anything else. Do not touch the `args` global's declaration —
there isn't one to touch; it's a harness-provided binding.

**0b. `FINDINGS_SCHEMA`/`FIX_RESULT` are declared with `const` *after*
the Tasks-phase loop that can call `reviewGate()`.** `reviewGate()`
(defined further down, function declarations hoist so this part is
fine) references `FINDINGS_SCHEMA`/`FIX_RESULT` inside its body. But
`const` bindings don't hoist their value — only the name enters a
temporal dead zone until the declaration line actually executes. The
top-level `for (const group of groups)` loop (line 144, right after
`phase('Tasks')` at line 143) calls `reviewGate()` for any group
containing a `milestoneEnd: true` task —
and since nearly every real plan has exactly one such task (usually
the last one), this fires on essentially every run that reaches it,
throwing `Cannot access 'FINDINGS_SCHEMA' before initialization`
before a single `agent()` call for that gate is ever made.

**Fix:** move the `const FINDINGS_SCHEMA = {...}` and `const FIX_RESULT
= {...}` blocks (currently lines 187–207, immediately after
`runParallelGroup`'s closing brace) to before the `phase('Tasks')` line
(currently line 143) — e.g. directly after the `TASK_RESULT` schema
declaration (after line 50). No other content changes; this is a pure
reorder.

**Acceptance (both 0a and 0b):**
- `node --check claude-new/execute-plan/workflows/run-plan.mjs` exits 0
- `! grep -q 'args\.' claude-new/execute-plan/workflows/run-plan.mjs` exits 0 (zero remaining bare `args.` references — note plain `grep -c` exits 1, not 0, when the count is zero, so don't use `-c` for this check)
- `test "$(grep -n '^const FINDINGS_SCHEMA' claude-new/execute-plan/workflows/run-plan.mjs | head -1 | cut -d: -f1)" -lt "$(grep -n \"^phase('Tasks')\" claude-new/execute-plan/workflows/run-plan.mjs | head -1 | cut -d: -f1)"` exits 0 (FINDINGS_SCHEMA declared before the Tasks-phase loop)

## Requirement 1: checkpoint should reuse reviewGate's fix-cycle loop

**Current behavior:** `checkpoint` (around line 253 in the current
file) is a single `agent()` call returning `TASK_RESULT` (bare
`status: done|blocked`). If lint/build/test/`/verify` don't all pass,
the script hard-throws (`if (checkpoint?.status !== 'done') throw new
Error(...)`) and the entire run dies. Contrast with `reviewGate()`,
which turns findings into structured objects (`FINDINGS_SCHEMA`) and
runs each blocking one through an automatic fix-cycle loop (up to
`maxFixCycles`) before giving up.

**Impact observed:** in the kb v1 run, the checkpoint's `/verify` pass
caught two real regressions (a startup crash on a fresh vault; a CLI
timeout misconfigured against the server's own budget). The run just
died. A human had to read the failure message, diagnose, patch the
code by hand, and manually invalidate the checkpoint agent's cache
(since its prompt is static and would otherwise replay the same
cached failure on resume) before the run could continue.

**Required change:** `checkpoint` must return findings in the
`FINDINGS_SCHEMA` shape instead of a bare `TASK_RESULT`, and any
`critical`/`major` finding it returns must go through the same
fix-cycle loop `reviewGate()` already implements (reuse that logic;
do not fork a second copy of it). Only hard-throw if a finding remains
unfixed/unaccepted after the fix-cycle budget is exhausted, exactly as
`reviewGate` already does for its own findings.

**Acceptance:**
- `node --check claude-new/execute-plan/workflows/run-plan.mjs` exits 0
- Reading the script, `checkpoint`'s findings pass through the same
  fix-cycle code path as `reviewGate`'s findings (no duplicated
  fix-cycle logic — refactor `reviewGate`'s inner loop into a shared
  function both call)
- The harness smoke test (Requirement 3) still passes after this change

## Requirement 2: adversarial findings must gate the verdict

**Current behavior:** the adversarial review step (around line 301)
computes `adversarial = { status: 'ran', findings: adv?.findings ?? []
}` and this is *only* ever appended to the final report object
verbatim — it is never merged into `state.findings`, and the verdict
computation (`blockingOpen = state.findings.filter(f => f.status ===
'open' && ['critical','major'].includes(f.severity))`, around line 315)
never sees it. A `critical` adversarial finding therefore cannot fail a
run, cannot trigger a fix cycle, and cannot even flip `PASS` to `WARN`
— it is pure prose in the report, and reading it is entirely optional.

**Impact observed:** in the kb v1 run, this let two **critical** bugs
ship under a `WARN` verdict (`bootstrap_collections()` never called on
startup — a fresh Qdrant instance has no collections and every
search/ask/index operation fails; a CLI command hardcoding a blank
destination — every captured note landed in the vault root, outside
the reindex system's scope entirely). Both were found only because a
human happened to read the adversarial section of the report by hand
and asked follow-up questions. This is the single most damaging gap of
the four — a "WARN" verdict is supposed to mean "safe modulo known
minor caveats," not "safe modulo two things that will break for every
real user."

**Required change:** merge `adversarial.findings` with severity
`critical` or `major` into `state.findings` (tagged with their origin,
e.g. `where: 'adversarial'`) *before* the verdict computation, and run
them through the same fix-cycle loop as Requirement 1's `checkpoint`
findings and `reviewGate`'s own findings. Minor/nit adversarial
findings may remain report-only, consistent with how minor/nit
findings from `reviewGate` are already handled.

**Acceptance:**
- `node --check claude-new/execute-plan/workflows/run-plan.mjs` exits 0
- Reading the script, a `critical`/`major` adversarial finding is
  reachable from the same code path that computes `blockingOpen` — i.e.
  it is provably capable of flipping the verdict, not just present in
  the report object
- The harness smoke test (Requirement 3) still passes after this change

## Requirement 3: run the skill's own smoke test (finally)

Follow `claude-new/execute-plan/tests/smoke.md` exactly, in a fresh
interactive session, against the `~/repos/skills-test-harness/claude-test`
harness (or an equivalent fresh consumer repo) — not against
`savviety-skills` itself, since the smoke test's toy fixtures assume a
clean target repo. Record the outcome (PASS criteria are listed in
`smoke.md`) in `claude-new/README.md`'s `## Validation status` section.
This has never been run before; it is the actual acceptance gate for
promoting `claude-new/` into `manifest.json`, separate from and in
addition to Requirements 0–2 above.

**Acceptance:**
- Every PASS criterion in `claude-new/execute-plan/tests/smoke.md`
  is met, including the kill+`resumeFromRunId` replay check and the
  `/execute-prd` toy-PRD write_scope-overlap rejection check
- `claude-new/README.md` records the result

## Non-goals

- Do not promote `claude-new/` into `manifest.json` as part of this
  work — that's a separate PR per `claude-new/HANDOFF.md`'s own plan,
  gated on Requirement 3 passing.
- Do not touch `claude/execute-plan` or `claude/execute-prd` (the old,
  currently-installed versions) — `claude-new/` is a parallel staging
  tree per existing project convention.
- Do not attempt to fix every finding from the kb v1 postmortem's
  recommendation list beyond R-001/R-002/R-003 (this doc's
  Requirements 2/1/0b+3 respectively) — R-004/R-005/R-006 are
  plan-authoring/AERS-rubric recommendations for a separate piece of
  work, not runtime bugs in `run-plan.mjs` itself.
