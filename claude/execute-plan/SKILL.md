---
name: execute-plan
description: "Use when the user has a written implementation plan file (typically produced by /execute-prd, in the plan-format contract) and wants it executed — phrases like 'execute the plan', 'run docs/plans/X.md', 'resume the plan'. Not for writing plans (use /execute-prd) or trivial single-file edits."
---

# /execute-plan — Plan Executor (judgment layer)

The deterministic runtime — task loop, retries, worktree lanes,
review-fix cycles, report assembly — lives in
`workflows/run-plan.mjs` and runs via the Workflow tool. This skill
owns everything that requires judgment: preflight gates, ambiguity
handling, disposition decisions, verdict interpretation, postmortem.

## Preflight (all gates must pass before the workflow launches)

1. **Repo-delivery contract.** Read `CLAUDE.md ## Commands` per
   `_internal/repo-delivery`. Missing → halt with:
   `Repo missing required CLAUDE.md ## Commands section.`
2. **Validate plan — refuse contract.** Run `/validate-plan <path>`.
   `FAIL` → refuse to execute; surface findings. Only an explicit
   human `--force` overrides, and its use goes in the final report.
3. **Workspace.** Refuse to run on `default_branch`. If needed,
   create `execute-plan/<slug>-<timestamp>` off `default_branch`.
   Record `baseSha` (HEAD) and `planSha` (sha256 of the plan file).
4. **Pre-execution clarification (codebase-aware).**

   **This is NOT a re-validation of the plan.** `/validate-plan`
   (gate 2) has already passed — the plan's structure, acceptance
   criteria, and closed decisions are fine. Gate 4 is a separate,
   codebase-aware gate that fires only when the plan, *read against
   the actual repo state*, has more than one reasonable execution. It
   cannot run until the repo is present, which is why it happens here
   and not inside `/validate-plan`.

   When gate 4 pauses, surface it with this framing so the operator
   does not read it as "the plan is bad":

   ```
   Plan validation: PASS (gate 2).
   Pre-execution clarification needed:
     <N> point(s) in the plan map to more than one thing in this codebase.
     The plan itself is fine — I need you to pick a referent before I
     start coding, so I don't silently guess wrong.
   ```

   Never phrase gate 4 output as "the plan tasks are not atomic" or
   "the plan has problems" — that contradicts the verdict that just
   passed and is the single biggest UX defect this flow has shipped.

   The executor must distinguish **ambiguity** (→ pause or abort) from
   **uncertainty** (→ try). An ambiguity is a point where the plan has
   more than one reasonable reading *given the repo* and picking silently
   would produce code that might not match the author's intent. The
   heuristic:

   > Would a human reading the plan and seeing what I'm about to do say
   > *"yes, that's obviously what I meant"*? If yes, proceed. If no, pause.

   **Three categories that count as ambiguity**

   1. **Referent ambiguity** — the plan names a thing and the repo has
      more than one candidate. *"Modify the user service"* when
      `src/services/user.ts`, `src/api/user/controller.ts`, and
      `src/models/user.ts` all plausibly fit.
   2. **Existing-state ambiguity** — the plan prescribes an addition and
      the repo already has something overlapping. *"Add a rate limiter"*
      when IP-level throttling is already present; add-on, replace, or
      stack are all defensible.
   3. **Scope-boundary ambiguity** — the plan prescribes a change and the
      change's natural boundary crosses something the plan didn't mention.
      *"Refactor the auth middleware into a service class"* when the
      middleware calls a helper in a sibling module and is hooked by a
      logger.

   **What is NOT ambiguity (proceed, do not pause)**

   - *"I don't know how to implement this."* That's an executor-skill
     issue; try.
   - *"There's a better way than the plan specifies."* That's scope
     discipline; follow the plan, log a `minor` finding.
   - General uncertainty about outcomes — not the same as the plan having
     multiple reasonable readings.

   Record every ambiguity — answered or aborted — as a `plan-ambiguity`
   finding in the final report.

   Interactive session → surface each ambiguity with AskUserQuestion
   and record the answer as a closed decision appended to the plan
   (this changes planSha — recompute). Autonomous session → halt
   listing the ambiguities as open questions.

## Launch the runtime

Invoke the Workflow tool:

    Workflow({
      scriptPath: "<this-skill-dir>/workflows/run-plan.mjs",
      args: {
        planPath, planSha, baseSha, branch,
        commands: { install, lint, build, test, defaultBranch },  // from ## Commands
        flags: { maxRetries: 20, maxFixCycles: 3, acceptRisk: [<from --accept-risk>], adversarial: "<auto|always|never>" },
        timestamp: "<ISO now>"
      }
    })

`<this-skill-dir>` is the `Base directory for this skill:` path
printed when this skill loaded. `run-plan.mjs` is a Workflow-tool
script, not a Node module: pass its absolute path as `scriptPath` and
nothing else — do not run it with `node`, `import` it, or paste its
contents into `script`. This instruction is the operator's opt-in to
multi-agent orchestration; no further confirmation is needed. If the
session has no Workflow tool, halt and say so — do not emulate the
script with the Agent tool.

While it runs, do not implement tasks yourself — the workflow owns
execution. On a thrown error the run is preserved (worktree branches
and commits stay); diagnose, then resume with the same scriptPath and
`resumeFromRunId` from the failed run — completed agent calls replay
from cache.

## Interpreting the result

The workflow returns the report object. Write
`execution-report.json` verbatim and render `execution-report.md`
from it (tables: per-task, findings with disposition statuses,
deviations, retry stats).

Verdict rules (apply the disposition rubric in
`_internal/disposition/SKILL.md`; `open` is not a valid end-state):

- **PASS** — all tasks done; every critical/major finding is `fixed`
  or `accepted-risk`; only `minor`/`nit`/`plan-deviation`/`plan-ambiguity`
  findings may remain (in terminal statuses); checkpoint passes; plan
  aligned.
- **WARN** — all tasks done; some `minor` / `nit` findings remain in
  terminal status (`open`, `defer`, `disagree-with-evidence`); any
  `plan-deviation` findings have a terminal disposition
  (`disagree-with-evidence`, `defer`, or `accepted-risk`); no
  blocking criticals/majors; checkpoint passes.
- **FAIL** — any `critical` or `major` finding ends `open`;
  any `plan-deviation` or `plan-ambiguity` ends `open` (these
  severities demand explicit disposition); checkpoint fails; or
  plan alignment has undispositioned gaps.

Plan-deviations that are terminally dispositioned (including
`accepted-risk` via `--accept-risk`) do **not** push the verdict to
FAIL. They count as WARN.

The professional grade does **not** affect the verdict. A `junior`-graded
component still PASSes if it's bug-free. The grade is informational — the
team decides what to do with it.

Disposition vocabulary and end-state rules are canonical in
`_internal/disposition/SKILL.md`; the workflow emits statuses from
that vocabulary and this skill never invents new ones.

## Decision records

Write records per `_internal/decision-record/SKILL.md` for choices a
future run could plausibly reverse — ambiguity resolutions from
preflight gate 4 and accepted-risk deviations always qualify.

## Postmortem

Fire when verdict is WARN/FAIL, the retry budget was exhausted, or
any deviation ended accepted-risk. Output lands next to the execution
report; append to `docs/postmortems/index.json`.

### Markdown structure (full mode)

```
# Postmortem

## Run reference
- **Plan:** <plan-file>
- **Verdict:** <verdict>  Gate: <gate_state>
- **Branch / base / head:** ...
- **Trigger:** <which auto rule fired, or "--postmortem=always">
- **Mode:** full | lightweight

## What happened
<2–4 sentence narrative — not a chat transcript, not a restatement
of findings.>

## What worked
<Process strengths observed: which gates caught what, which auto-fix
cycles converged cleanly, where the closed decisions saved time.>

## What broke down

### Tool and skill usage
<Which gates fired or didn't fire, and whether that was correct.
Threshold issues (e.g. adversarial review missed a 187-line auth diff
because the threshold is 200). Skills invoked at the wrong time, or
not invoked when they should have been. Repo-delivery flags or
`adversarial_triggers` paths that need tuning.>

### Requirements fit
<Ambiguity in the source PRD/AERS that drove rework. Plan-deviations
or plan-ambiguities whose root cause was an unsettled product
decision. Closed decisions that should have existed but didn't.
aers-readiness rubric items that the source missed.>

## What the process missed
<Gaps only visible in hindsight. Coverage holes (link to `unproved`
rows). Reviewer blind spots. Plan structure that hid risk.>

## Recommendations
<Specific, actionable. Each recommendation MUST cite a target from
the taxonomy below so the recommendation can aggregate across runs.
Free-text recommendations that don't aggregate are a bug.>

| # | Target | Type | Summary |
|---|---|---|---|
| 1 | `_internal/disposition` | tune-threshold | Disposition loop allowed 3 cycles where 2 would have caught the same fix |
| 2 | `closed-decisions/auth/session-cookie-name` | new-decision | Session cookie name was re-debated this run; capture as closed decision |
```

In `lightweight` mode, omit `What worked` and the two named lenses.
The remaining shape is `What happened` → `What broke down` (free
form) → `Recommendations` (still structured).

### Recommendation taxonomy

Every recommendation row in the markdown table corresponds to a
structured object in `postmortem.json`. The `target` and `type` fields
use a fixed vocabulary so cross-run aggregation works.

**`target` vocabulary** (where the recommendation lands):

| `target` value | What it points at |
|---|---|
| `_internal/disposition` | The disposition rubric |
| `_internal/repo-delivery` | The repo-delivery contract / `## Commands` schema |
| `_internal/<other>` | Any other rubric in the skill library |
| `closed-decisions/<category>/<slug>` | A new or updated closed decision fragment |
| `claude-md/commands` | The repo's `CLAUDE.md ## Commands` section |
| `claude-md/conventions` | The repo's `CLAUDE.md` conventions section |
| `adversarial-triggers` | The `adversarial_triggers` glob list |
| `auto-accept-deviations` | The `auto_accept_deviations` category list |
| `plan-template` | The plan author's template (drives `/execute-prd` step 7) |
| `aers-readiness` | The AERS readiness rubric |
| `execute-plan-skill` | This skill's own behaviour (gates, phases, defaults) |
| `execute-prd-skill` | The `/execute-prd` skill's behaviour |
| `domain-review-profile` | A `domain-review` profile (`breakpoint` or `full`) |
| `process-doc/<name>` | Any project-level process doc not covered above |

If a recommendation genuinely doesn't fit, use `target: other` and put
the intent in `summary` — but treat that as a smell, not a release
valve. Repeated `other` values are a sign the taxonomy needs an entry.

**`type` vocabulary** (what kind of change):

| `type` value | Meaning |
|---|---|
| `tune-threshold` | Numeric threshold needs adjustment (line counts, retry counts, timeouts) |
| `tune-trigger` | A glob, signal, or condition that controls when something fires |
| `new-decision` | Add a closed decision capturing a settled fact |
| `update-decision` | Modify an existing closed decision |
| `new-convention` | Add a project convention to CLAUDE.md |
| `add-rubric-rule` | Extend an existing rubric with a new rule |
| `tighten-gate` | Make an existing gate stricter |
| `relax-gate` | Make an existing gate less strict (rare; needs evidence) |
| `add-gate` | Introduce a new gate or phase |
| `remove-gate` | Remove a gate that produces no signal |
| `improve-prompt` | Reword an instruction passed to a worker or reviewer |
| `documentation` | The skill or process is correct but the docs don't reflect reality |

### JSON schema (postmortem.json)

```json
{
  "run": "2026-05-05-143000",
  "plan_file": "docs/plans/<plan-slug>.md",
  "verdict": "WARN",
  "gate_state": "completed-with-accepted-risk",
  "trigger": "unproved-rows",
  "mode": "full",
  "recommendations": [
    {
      "id": "R-001",
      "target": "adversarial-triggers",
      "type": "tune-threshold",
      "summary": "Adversarial threshold of 200 lines missed a 187-line auth diff",
      "evidence": "execution-report.json#findings.F-014",
      "actionable": true,
      "confidence": "high"
    }
  ],
  "headline": "<one-line summary, copied from the highest-confidence actionable recommendation>"
}
```

`actionable: true` means a future skill could mechanically apply the
change. `confidence: high|medium|low` lets `/process-tune` weight
recurring recommendations.

### Cross-run aggregation

After writing `postmortem.md` and `postmortem.json`, append a row to
the project-level postmortem index:

- **Path:** `docs/postmortems/index.json` (relative to the repo root,
  not the run folder).
- **Append, never rewrite.** The index is an event log; old rows are
  immutable evidence even if the recommendation later proved wrong.
- **Schema:**
  ```json
  [
    {
      "run": "2026-05-05-143000",
      "run_folder": "docs/runs/2026-05-05-143000/",
      "plan_slug": "<plan-slug>",
      "verdict": "WARN",
      "gate_state": "completed-with-accepted-risk",
      "trigger": "unproved-rows",
      "recommendations": [
        {
          "id": "R-001",
          "target": "adversarial-triggers",
          "type": "tune-threshold",
          "summary": "...",
          "actionable": true,
          "confidence": "high"
        }
      ]
    }
  ]
  ```

If `docs/postmortems/index.json` does not exist, create it as `[]`
before appending. Do not gate on the directory existing — create it.

`/process-tune` (the symmetric consumer skill) reads this index,
groups by `target` + `type`, and proposes concrete artefact edits when
the same recommendation appears across multiple runs.

### Hard rules

- **Not a second requirements document.** Do not restate scope.
- **Not a chat-transcript summary.** No turn-by-turn replay.
- **Not a restatement of review findings.** Findings are in the
  execution report; postmortem analyses *the process around them*.
- **Not a blame document.** No "the model should have known" framing.
- **Length cap:** target one page (full mode) or half a page
  (lightweight). A long postmortem signals the run itself was
  unrecoverable and the next action is human review, not a longer
  document.
- **Recommendations must use the taxonomy.** Free-text targets that
  bypass the `target`/`type` vocabulary defeat aggregation. If the
  taxonomy doesn't fit, the taxonomy needs extending — not bypassing.

## Enforcement notes (not prose rules — actual config)

Destructive git commands are denied by `settings.template.json`
permissions (`git reset --hard`, `git push --force*`, `git clean -f`,
`git branch -D`). This skill assumes those rules are installed; it
does not restate them as instructions.

## Contract

- **Inputs:** `<path>` to a plan file in the `_internal/plan-format`
  contract; optional `--force` (override a `/validate-plan` FAIL),
  `--accept-risk <category>`, `--adversarial <auto|always|never>`, and
  `resumeFromRunId` when resuming a failed run. Calls `/validate-plan`
  (preflight gate 2) and the `workflows/run-plan.mjs` Workflow script,
  which owns the task loop. Consults `_internal/repo-delivery`,
  `_internal/disposition`, and `_internal/decision-record`.
- **Preconditions:** the session has the Workflow tool; repo has a
  `CLAUDE.md ## Commands` section; the plan validates (or a human
  `--force` is explicit and recorded); the working branch is not
  `default_branch`.
- **Outputs:** `execution-report.json` written verbatim from the workflow
  result plus `execution-report.md` rendered from it; decision records for
  choices a future run could reverse; a postmortem plus a
  `docs/postmortems/index.json` entry when the verdict is WARN/FAIL, the
  retry budget was exhausted, or any deviation ended `accepted-risk`.
- **Postconditions:** a PASS / WARN / FAIL verdict is stated against the
  rules above; no `critical` or `major` finding is left `open` without the
  verdict being FAIL; every `plan-ambiguity` resolved or raised in
  preflight gate 4 appears in the report; commits and worktree branches
  from a thrown run are preserved for resume.
- **Failure modes:** missing `CLAUDE.md ## Commands` → halt; `/validate-plan`
  FAIL without `--force` → refuse to execute; on `default_branch` → refuse;
  preflight-gate-4 ambiguity in an autonomous session → halt listing the
  open questions as `plan-ambiguity` findings; no Workflow tool → halt and
  say so, never emulate `run-plan.mjs` with the Agent tool.

## When NOT to Use

- No plan exists — use `/execute-prd` (PRD input) or
  superpowers:writing-plans (ad-hoc).
- Plan doesn't follow the plan-format contract —
  superpowers:executing-plans is the lighter general executor.
- Trivial single-file change — edit directly.
