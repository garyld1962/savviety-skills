---
slug: execute-plan-checkpoint-adversarial-gating
source_prd: docs/superpowers/specs/2026-07-07-execute-plan-runtime-fixes.md
intent: Route checkpoint and adversarial-review findings through the same fix-cycle loop reviewGate already uses, so critical/major findings from either source can gate the run verdict instead of being silently dropped or hard-crashing the run.
type: bug
---

# execute-plan runtime: checkpoint + adversarial verdict gating

**Source:** docs/superpowers/specs/2026-07-07-execute-plan-runtime-fixes.md, Requirements 1 and 2 (Requirement 0 was applied manually and committed in `2925bc8`; Requirement 3 is a separate manual smoke-test gate, not a task in this plan — see Non-goals).

## Closed Decisions

- Shared fix-cycle function: the inline per-finding loop currently in `reviewGate` is extracted into `async function gateFindings(rawFindings, where)`, reused by `checkpoint` and the adversarial gate (full behavior specified in Task 1 below).
- checkpoint call shape: checkpoint's `agent()` call returns `FINDINGS_SCHEMA` instead of `TASK_RESULT`, guarded by an explicit null-result check so a failed agent call is never silently treated as zero findings (full behavior specified in Task 1 below).
- Adversarial call shape: `adversarial.findings` passes through `gateFindings(adversarial.findings, 'adversarial')` before verdict computation, with no severity pre-filtering at the call site (full behavior specified in Task 2 below).
- Self-hosting mirror: `claude-new/execute-plan/workflows/run-plan.mjs` and its overlay copy at `.claude/skills/execute-plan/workflows/run-plan.mjs` are edited identically within the same task, per the Requirement 0 precedent in commit `2925bc8`.

## Non-goals (carried from source PRD)

- Requirement 3 (running `claude-new/execute-plan/tests/smoke.md` against a fresh consumer repo) is **not** a task here — it requires a fresh interactive session against `~/repos/skills-test-harness/claude-test`, which this plan's automated task runner cannot perform. Run it manually after this plan's verdict is PASS/WARN, then record the result in `claude-new/README.md`'s `## Validation status` section per the source PRD.
- Do not promote `claude-new/` into `manifest.json` — gated on Requirement 3, out of scope here.
- Do not touch `claude/execute-plan` or `claude/execute-prd` (old installed versions).

## Task 1: Extract gateFindings; checkpoint reuses it

```yaml
depends_on: []
write_scope:
  - claude-new/execute-plan/workflows/run-plan.mjs
  - .claude/skills/execute-plan/workflows/run-plan.mjs
milestone_end: false
```

Refactor `reviewGate`'s inline per-finding loop (currently the `for (const f
of findings) {...}` block inside `reviewGate`, roughly lines 225–247 as of
commit `2925bc8`) into a standalone `async function gateFindings(rawFindings,
where)`:

- Maps each item of `rawFindings` to `{ ...f, where, status: 'open' }`.
- For each mapped finding: non-blocking (`minor`/`nit`/`plan-deviation`)
  severities push straight to `state.findings` and continue. Blocking
  (`critical`/`major`) severities check `cfg.flags?.acceptRisk` first, then
  run the existing fix-cycle loop (up to `cfg.flags?.maxFixCycles ?? 3`,
  calling `spendRetry`), then push to `state.findings`.
- After the loop, if any finding in this batch ended `status === 'open'`,
  throw the existing error message (`Finding ${f.id} (${f.severity}) still
  open after fix cycles at ${where}. ...`), unchanged from current text.
- `reviewGate(profile, where)` keeps its existing `agent()` call that
  produces `findings`, then simply does `return gateFindings(findings,
  where)` — no duplicated loop logic remains in `reviewGate`.

Then rewrite the `checkpoint` block (currently the single `agent()` call
around line 256 using `TASK_RESULT`, plus its `if (checkpoint?.status !==
'done') throw ...`):

- Change the agent call's `schema` to `FINDINGS_SCHEMA`. Update the prompt
  so the agent reports lint/build/test/`/verify` failures as findings
  (`severity: 'critical'` for a broken build or failing tests, `severity:
  'major'` for a lint or `/verify` failure) instead of a bare done/blocked
  status; an empty `findings` array means everything passed.
- Add `if (!checkpoint) throw new Error('Checkpoint agent failed to return a
  result')` immediately after the call — a null agent result must not be
  silently treated as zero findings.
- Replace the old `if (checkpoint?.status !== 'done') throw ...` line with
  `await gateFindings(checkpoint.findings ?? [], 'checkpoint')`.

Copy the finished file verbatim from `claude-new/execute-plan/workflows/run-plan.mjs`
to `.claude/skills/execute-plan/workflows/run-plan.mjs` (the self-hosting
overlay) so both are identical — this task owns both paths.

**Acceptance:**
- `bin/check-workflow-syntax claude-new/execute-plan/workflows/run-plan.mjs .claude/skills/execute-plan/workflows/run-plan.mjs` exits 0
- `diff claude-new/execute-plan/workflows/run-plan.mjs .claude/skills/execute-plan/workflows/run-plan.mjs` exits 0 (overlay mirrors canonical exactly)
- `grep -c "async function gateFindings" claude-new/execute-plan/workflows/run-plan.mjs` outputs exactly `1`
- `grep -c "cycle <= maxCycles" claude-new/execute-plan/workflows/run-plan.mjs` outputs exactly `1` (fix-cycle loop exists in only one place, proving `reviewGate` and `checkpoint` share it rather than each having their own copy)
- `! grep -q "checkpoint?.status !== 'done'" claude-new/execute-plan/workflows/run-plan.mjs` exits 0 (old bare hard-throw is gone)
- `grep -B8 "label: 'checkpoint'" claude-new/execute-plan/workflows/run-plan.mjs | grep -q "schema: FINDINGS_SCHEMA"` exits 0 (the checkpoint call site itself uses `FINDINGS_SCHEMA`, not just the file somewhere)

## Task 2: Adversarial findings gate the verdict

```yaml
depends_on: [1]
write_scope:
  - claude-new/execute-plan/workflows/run-plan.mjs
  - .claude/skills/execute-plan/workflows/run-plan.mjs
milestone_end: true
```

In the adversarial-review block (currently right after the plan-alignment
block, before `phase('Report')`): after computing `adversarial = { status:
'ran', findings: adv?.findings ?? [] }`, add `await
gateFindings(adversarial.findings, 'adversarial')` — called only in the
branch where adversarial review actually ran (i.e. inside the same `if
(cfg.flags?.adversarial === 'always' || ...)` block, after the `adversarial =
...` assignment), *before* `phase('Report')` and before the `blockingOpen`
computation. Do not filter by severity at the call site — `gateFindings`
(from Task 1) already discriminates blocking vs non-blocking internally,
exactly as it does for `reviewGate` and `checkpoint` findings.

No other change to `blockingOpen`/`verdict` computation is needed — since
`gateFindings` already pushes adversarial findings into `state.findings`,
the existing `blockingOpen = state.findings.filter(...)` line already sees
them.

Copy the finished file verbatim to `.claude/skills/execute-plan/workflows/run-plan.mjs`, same as Task 1.

**Acceptance:**
- `bin/check-workflow-syntax claude-new/execute-plan/workflows/run-plan.mjs .claude/skills/execute-plan/workflows/run-plan.mjs` exits 0
- `diff claude-new/execute-plan/workflows/run-plan.mjs .claude/skills/execute-plan/workflows/run-plan.mjs` exits 0
- `test "$(grep -n 'gateFindings(adversarial.findings' claude-new/execute-plan/workflows/run-plan.mjs | head -1 | cut -d: -f1)" -lt "$(grep -n \"phase('Report')\" claude-new/execute-plan/workflows/run-plan.mjs | head -1 | cut -d: -f1)"` exits 0 (adversarial gating happens before the Report phase / verdict computation)
- `grep -c "async function gateFindings" claude-new/execute-plan/workflows/run-plan.mjs` still outputs exactly `1` (Task 2 reused Task 1's function, did not add a second one)
