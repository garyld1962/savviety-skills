---
name: execute-plan
description: "Execute a written implementation plan end-to-end with staged reviews: validate-plan → per-task build/test → breakpoint review at milestones → full code review + professional craft grading at PR boundary → optional adversarial review. Use when you have a written plan file ready to execute, want per-task build/test cycles plus staged code reviews, or want a seniority-calibrated craft grade. Do NOT use when no plan exists yet (write a plan first), for trivial single-file changes (make the edit directly), or when you only want a quick quality gate (use checkpoint instead)."
---

# /execute-plan — Plan Executor with Staged Reviews

**Purpose:** Execute a written implementation plan with a staged review sequence:
validate-plan → per-task build/test → breakpoint review at each milestone → full
code review + professional (craft) review at the PR boundary → optional
adversarial review.

## When to Use

- You have a written plan file ready to execute.
- You want per-task build/test cycles plus staged code reviews.
- You want a seniority-calibrated craft grade on the final output.

## When NOT to Use

- No plan exists yet — write a plan first.
- Trivial single-file change — just make the edit directly.

## Arguments

| Argument | Description |
|---|---|
| `<path>` | Path to the plan file (optional; if omitted, finds the most recent `.md` in `docs/plans/`). |
| `--interactive=<yes\|no\|auto>` | How to handle execution-time ambiguity (see Phase 1.5). Default: `auto`. `yes` = pause and ask on every ambiguity; use when a human is supervising. `no` = batch / CI mode; never prompt; on ambiguity, abort cleanly and log the question in the final report's `## Open Questions` section. `auto` = detect TTY; prompt if present, otherwise abort. |
| `--force` | Bypass the refuse-on-FAIL contract (see Phase 0). `validate-plan` returning FAIL still runs `/execute-plan` anyway. **For humans only; never set by the harness or by default.** Use is logged prominently in the final execution report so the bypass is auditable. |
| `--resume` | Resume a previously aborted run instead of starting fresh. Scans commits on the current branch for `Task N from <plan-file>` footers, ignoring `review(` auto-fix commits. Verifies all prior task commits share the same `Plan-SHA`; if the current plan file's SHA has drifted, refuses to resume. After confirming matching Plan-SHA, re-runs the last milestone's breakpoint review against the accumulated diff for fresh scrutiny, then proceeds at the next task. Prior abort tags are preserved as audit markers. |
| `--create-branch` | In Phase 0c, create a feature branch even if HEAD is already on a non-default branch. Useful when the caller wants a clean slate. Branch is named `execute-plan/<plan-slug>-<YYYYMMDD-HHMM>` off `default_branch`. |
| `--max-retries=<N>` | Override the global retry budget for this run (see "Retry budget" below). Default: 20. |
| `--max-minutes=<N>` | Override the wall-clock budget for this run. Default: 60. |
| `--accept-risk=<finding-id>` | Explicitly accept a critical or major finding (see `_rubrics/disposition`). Can be repeated for multiple findings. **For humans only** — never set by the harness. Each use is logged in the final report with the finding it accepted. |
| `--adversarial=<auto\|always\|never\|ask>` | When to run the adversarial review stage (Phase 3e). Default: `auto`. `auto` = fires when the cumulative diff is ≥200 lines OR touches a path listed in `adversarial_triggers`; otherwise skipped silently. `always` = always runs regardless of diff size or paths. `never` = never runs; no prompt, no invocation. `ask` = interactive legacy behaviour; prompt the user per the legacy flow. Use `ask` only when a human is supervising. |

### `adversarial_triggers`

An optional list of globs whose modification causes `--adversarial=auto`
to fire regardless of diff size. Read from the repo's CLAUDE.md
`## Commands` section (see `_rubrics/repo-delivery`). If absent, the
default list is used:

```
adversarial_triggers:
  - src/auth/**
  - src/payments/**
  - migrations/**
  - **/crypto/**
```

`adversarial_triggers` is defined in exactly one place (the repo's
CLAUDE.md or the default above); do not duplicate it inside individual
plans.

## Workflow

### Phase 0: Preflight

Two gates before any execution work:

**0a. Repo-delivery contract.** Read the `## Commands` section of the
repo's `CLAUDE.md` per `_rubrics/repo-delivery`. If it's missing, fail
fast with this exact message and stop — do not infer, do not guess,
do not fall back to manifest detection:

```
Repo missing required CLAUDE.md ## Commands section.
See _rubrics/repo-delivery for the schema.
```

The `lint` / `build` / `test` / `default_branch` / `package_manager`
fields drive every subsequent phase. The rubric is the schema
definition; the message above is the exact user-facing string.

**0b. Validate plan — refuse contract.** Invoke `/validate-plan <path>`.
If it returns `VERDICT: FAIL`, **refuse to execute** and surface the
findings. Do not proceed under any circumstances except the explicit
`--force` override (see below). This refusal is non-negotiable — a bad
plan silently guessed through is the single biggest correctness risk
this flow exists to prevent.

The `--force` escape hatch exists for humans who have evaluated the
findings and decided to proceed anyway. It requires the explicit
argument — the harness never sets it; no default triggers it. Its use
is recorded prominently in the final execution report:

```
WARNING — plan validation FAILED and was overridden with --force.
Outstanding findings from validate-plan:
  - [check N] ...
```

**0b.5. Tool-availability probe.** Between plan validation and workspace
preparation, verify that every command declared in the repo-delivery
`## Commands` schema actually resolves on the executor's PATH. Subagent
shells do not source interactive shell profiles, so toolchains managed
by `nvm`, `fnm`, `pyenv`, `rbenv`, `asdf`, `mise`, or similar must be
on PATH *before* any subagent is spawned or the run will fail opaquely
with "command not found" in a worker that the operator can't inspect.

Probe explicitly — do not rely on the parent shell's PATH:

```bash
command -v "<package_manager>"   # e.g. pnpm, npm, poetry, cargo
command -v "<lint_cmd first token>"
command -v "<build_cmd first token>"
command -v "<test_cmd first token>"
# JS projects only:
command -v node
```

If **any** probe fails, halt with this exact message and stop — do not
attempt to install, do not guess an alternative, do not fall back to a
different tool:

```
Required toolchain missing on PATH.
  Missing: <cmd-a>, <cmd-b>, ...
  Declared in: <repo>/CLAUDE.md ## Commands

Likely cause: node/pnpm/python managed by nvm/fnm/pyenv/asdf and the
PATH modification in your shell profile is not inherited by subagents.

Fix one of:
  1. Run /execute-plan from a shell where `command -v <pm>` succeeds
     AND the harness inherits that PATH. Most reliable: activate the
     toolchain version (e.g. `nvm use`, `pyenv shell <ver>`), then
     re-invoke.
  2. Add the absolute path (e.g. ~/.local/share/pnpm, ~/.nvm/versions/
     node/<ver>/bin) to CLAUDE.md alongside the ## Commands section
     so the executor can set PATH deterministically.
  3. Install the tool system-wide (outside a version manager) so it
     lives on a default PATH.
```

When probes pass, echo a one-line confirmation:
```
Toolchain probe OK: <pm> <pm-version>, node <node-version>, <test-runner>.
```

All subagent Bash invocations from this skill onwards MUST be spawned
via a login shell (`zsh -l -c "<cmd>"` or `bash -l -c "<cmd>"`) so the
same profile that populated PATH at probe time is populated again
inside the worker. Skills that dispatch workers via the Task tool must
surface this requirement in their spawn-context preamble.

**0c. Prepare workspace.** After Phase 0a (schema), Phase 0b (plan
validation), and Phase 0b.5 (tool probe) succeed, establish the branch
and baseline the run will operate on:

1. Read `default_branch` from the repo-delivery `## Commands` schema.
2. **Refuse to run on the default branch.** If
   `git rev-parse --abbrev-ref HEAD` equals `default_branch`, halt:
   ```
   /execute-plan refuses to run directly on the default branch
   (`<default_branch>`). Create a feature branch, or invoke with
   --create-branch to let execute-plan create one for you.
   ```
3. If invoked with `--create-branch`, or if HEAD is detached / in a
   special state, create and switch to a feature branch named
   `execute-plan/<plan-slug>-<YYYYMMDD-HHMM>` off `default_branch`.
   Otherwise, proceed on the current (non-default) branch.
4. Record the current commit SHA as `$EXECUTE_PLAN_BASE_SHA`.
   Every subsequent task commit carries `Base-SHA: <sha>` and
   `Plan-SHA: <plan-sha>` trailers so Phase 3d (plan alignment) and
   Task 3's `--resume` can reconstruct the run.
5. Record the active branch name for the failure-path preservation
   rules below.

#### Failure path — preserve, never destroy

On any unrecoverable failure — retry-budget exhaustion, a worker
refusing to continue, a review-fix spiral that can't converge,
validate-plan refusing mid-stream after `--force`:

1. Tag the last successful commit as
   `execute-plan/abort/<plan-slug>-<YYYYMMDD-HHMM>` so the abort point
   is locatable by name.
2. Leave the working branch intact. Leave the index intact. Do not
   stash, reset, or clean working-tree changes without explicit
   operator intent.
3. Surface:
   ```
   Run aborted. Branch preserved at <branch-name>.
   Last successful commit tagged: execute-plan/abort/<slug>-<timestamp>.
   Resume with: /execute-plan --resume <plan-file>
   ```
4. Exit non-zero so callers (CI, wrapping scripts) can detect abort.

Destructive git operations are **forbidden** in all code paths of this
skill:
- Never `git reset --hard`
- Never `git push --force` (push is out of scope anyway; Task 25's
  dogfood contract is local-only until the full flow is validated)
- Never `git branch -D` / `git branch --delete --force`
- Never `git clean -f` in the working tree
- Never force-overwrite tags

The principle: the caller loses no work on abort. A failed run is a
branch you can inspect, diff, cherry-pick from, or resume. It is never
a silently-discarded state.

### Decision records (cross-execution memory)

Unlike human engineers, LLMs accumulate no organic memory of
decisions defeated along the way. Without a deliberate memory medium,
every execution is knowledge-destroying — the next LLM touching the
same code starts cold and may reverse choices the previous execution
spent effort to make. Decision records fill that gap.

#### Record format

One markdown file per decision at:

```
docs/decisions/<plan-slug>/<NNNN>-<kebab-slug>.md
```

- `<plan-slug>` — the executing plan's `slug` frontmatter field.
- `<NNNN>` — zero-padded sequence number within that plan-slug.
- `<kebab-slug>` — short imperative: `0042-route-validation-at-controller`.

Frontmatter (required):

```yaml
---
id: YYYYMMDD-NNNN
plan: <plan-slug>
task: <task-id>
date: YYYY-MM-DD
files:
  - path/to/affected/file.ts
  - path/to/glob/**
tags: [routing, validation, ...]
supersedes: null           # or the id of the decision this replaces
superseded_by: null        # set when a later decision replaces this
---
```

Body sections, required in this order:
Context · Decision · Reasoning · Rejected alternatives · Consequences · Revisit if.

Detail:

1. **Context** — what the executor was doing; what the plan said.
2. **Decision** — what was chosen, stated as a complete imperative.
3. **Reasoning** — why; cite the options considered.
4. **Rejected alternatives** — each option considered with a one-line
   rejection reason.
5. **Consequences** — downstream effects. What now becomes easier, what
   becomes harder.
6. **Revisit if** — named triggers under which this decision should be
   reconsidered.

#### Index

Two artefacts under `docs/decisions/`:

- **`docs/decisions/INDEX.md`** — human-facing markdown with file globs → decision IDs.
- **`docs/decisions/index.json`** — machine-queryable counterpart for the read-trigger:

```json
[
  {
    "id": "20260419-0042",
    "files": ["src/services/auth.ts", "src/api/user/**"],
    "tags": ["routing", "validation"],
    "supersedes": null,
    "superseded_by": null,
    "path": "docs/decisions/user-validation-march/0042-controller-layer.md"
  }
]
```

Both files are updated whenever a record is written or superseded.

#### Write triggers

`execute-plan` writes a record on exactly these events:

- A `plan-ambiguity` is resolved (Phase 1.5) — clarification answered
  in interactive mode, or operator resolved on resume.
- A `plan-deviation` is dispositioned (Phase 3d) — the disposition and
  its rationale.
- A non-trivial design call the plan didn't prescribe is made: API
  shape, pattern choice, layer placement, library selection, state
  machine, concurrency model, etc.

**Filter rule to prevent noise.** Write a record ONLY when a
reasonable future LLM, seeing only the code, could plausibly reverse
the choice. Forced, trivial, or fully-plan-prescribed choices do NOT
get records. If in doubt, err toward not writing; the index is noise
when it records every comma.

#### Read trigger

At the start of each task's implementation (Phase 2b), before any
worker dispatch:

1. Compute the task's target file set from the plan.
2. Query `docs/decisions/index.json` for records where any `files`
   entry matches a target file (glob match).
3. Filter out records with `superseded_by != null`.
4. Read each matching record's full content.
5. Include them in the implementing worker's context with the
   directive: *"These decisions govern files you're about to modify.
   Do not reverse a non-superseded decision without raising a
   `plan-ambiguity` finding that cites the decision's ID. Workers who
   silently reverse prior decisions undo effort and introduce drift."*

#### Supersede mechanism

When a new decision contradicts an existing one:

1. Write the new record with `supersedes: <old-id>` in frontmatter.
2. Rewrite the old record's frontmatter: set `superseded_by: <new-id>`.
3. Neither record is deleted. The chain is traversable forward and
   backward, preserving audit history.
4. Update both `INDEX.md` and `index.json`.

#### Proliferation guard

`/code-review` flags any task that produces more than **5 decision
records** in a single execution as a `minor` finding
(`too-many-decisions`). The filter rule above is the first defence;
this is the backstop against noise accretion.

### Retry budget (global circuit breaker)

Local per-phase retries (build: max 3 attempts; test: max 3 attempts;
auto-fix cycles in Phase 2.5 / 3b: max 3 each) prevent obvious loops —
but they don't prevent a task from burning the whole session across
many cheap retries. The global retry budget is the circuit breaker.

#### Values, in order of precedence

1. Command-line: `--max-retries=<N>` / `--max-minutes=<N>`.
2. Repo-delivery `## Commands` `retry_budget:` block:
   ```
   retry_budget:
     max_total_retries: 20
     max_wall_clock_minutes: 60
   ```
3. Defaults: `max_total_retries: 20`, `max_wall_clock_minutes: 60`.

#### Counter semantics

The global retry counter increments on **every**:
- build retry (Phase 2c)
- test retry (Phase 2d)
- auto-fix cycle (Phase 2.5 breakpoint review)
- auto-fix cycle (Phase 3b full-review)

It does **not** increment on:
- successful first-try builds/tests
- phase transitions (e.g., moving from Task 1 → Task 2)
- validate-plan invocations
- review dispatches themselves (only their auto-fix follow-ups)

The wall-clock timer starts at Phase 0c (workspace prep) and runs
through Phase 4 (final report).

#### Exhaustion behaviour

When either budget is hit mid-run:

1. Stop immediately — do not start another retry or advance to the
   next task.
2. Follow the Phase 0c failure path: tag
   `execute-plan/abort/<plan-slug>-<YYYYMMDD-HHMM>`, preserve the
   branch.
3. Surface the exact message:
   ```
   Retry budget exhausted (<N> retries, <M> minutes).
   Aborted at Task <K>.
   Resume with: /execute-plan --resume <plan-file>
   ```
4. Exit non-zero.

The budget is meant as a circuit breaker, not a deadline. A run that
completes in 55 minutes with 18 retries is normal; a run that spends
60 minutes retrying the same task is stuck and needs a human.

### Resume semantics (`--resume`)

When invoked with `--resume`, `/execute-plan` picks up from the last
completed task of a prior run instead of starting fresh.

#### How resume detects prior state

1. Scan commits on the current branch for `Task N from <plan-file>`
   footers. Every completed task produced one of these in the prior run.
2. **Ignore commits whose subject starts with `review(`** — those are
   auto-fix commits from Phase 2.5 / 3b (see "Auto-fix commits" above),
   not task work. They must not inflate the completed-task count.
3. Extract the set of completed task numbers from the remaining commits.
4. For each task commit, read the `Plan-SHA: <sha>` trailer (written
   by Phase 0c). All task commits in the prior run must share the same
   `Plan-SHA`.

#### Plan-SHA drift refusal

If the current plan file's SHA differs from the `Plan-SHA` recorded in
prior task commits, **refuse to resume**:

```
Plan file has changed since the last run.
  Prior Plan-SHA: <sha-a>  (from commit <abbrev>)
  Current Plan-SHA: <sha-b>

Resuming would mix tasks authored under different plan versions.
Re-run from scratch on a new branch, or revert the plan change.
```

Refuse because the meaning of "Task N" is plan-file-dependent. A
changed plan may reorder, renumber, or reshape tasks, and resuming
blindly would produce a run that conflates two different plans'
intentions.

#### Resume flow

After confirming matching Plan-SHA:

1. Report: `Resuming <plan-file> at Task <N+1>/M. Skipping N completed tasks.`
2. Re-run the last milestone's breakpoint review against the diff
   accumulated so far (the codebase state is whatever survived the
   previous abort; it deserves fresh scrutiny).
3. If the breakpoint review raises any blocking finding, halt and ask
   the operator to disposition before continuing.
4. Proceed into Phase 2 at the next task.
5. Phase 3 (PR-boundary reviews) still runs as normal once all tasks
   complete.

#### Tags and cleanup

Abort tags (`execute-plan/abort/...`) from the prior run are not
deleted automatically — they remain as audit markers. A successful
resume may leave multiple abort tags on the branch; that's fine. The
operator can garbage-collect them manually with `git tag -d` after the
run ships.

### Phase 1: Load Plan

1. If no path argument, find the most recent `.md` in `docs/plans/`.
2. Parse the plan into an ordered task list. Tasks are numbered sections,
   headings, or checklist items.
3. Identify **milestones**: sections explicitly marked `## Milestone:` (or
   `### Milestone:`) in the plan, or a `milestones:` list in the plan's
   frontmatter. If neither exists, treat the end of every top-level `##`
   section as an implicit milestone.
4. Report: `Found N tasks across M milestones in <plan-file>. Starting execution.`
5. **Load Closed Decisions.** If the plan has a `## Closed Decisions`
   section, parse it. Resolve every `@closed-decisions/<category>/<slug>`
   reference by reading
   `<claude-working-root>/closed-decisions/<category>/<slug>.md`, where
   `<claude-working-root>` is the directory containing this
   `execute-plan/` skill (i.e. the library ships with the skill, not
   in the consumer repo). Inline the fragment's bullets into the
   working decision set. Cache the merged set for the whole run.

### Phase 1.4: Closed Decisions are tablestakes

Before each task's implementation (Phase 2b), pass the merged Closed
Decisions set to the implementing worker with this directive, verbatim:

> These are tablestakes. Do not propose alternatives, do not deliberate,
> do not surface them as ambiguity. Execute as stated. If a task's own
> spec contradicts a closed decision, raise a `plan-deviation` finding
> (see code-review/references/controller-guide.md) and halt — do not attempt to reconcile.

Closed decisions pre-empt Phase 1.5 ambiguity categories 2
(existing-state) and 3 (scope-boundary). If an ambiguity would have
fired but a closed decision disambiguates it, do not pause — the
closed decision is the resolution.

#### Template-copy fast path

If a task's spec is shaped *"scaffold from `templates/<name>/`"* (a
common pattern for project setup — framework scaffolding, boilerplate),
execute runs the copy as a one-shot:

1. Verify `templates/<name>/` exists (per the closed decision naming it).
2. Copy its contents into the destination under git.
3. Commit with the normal Task N footer.
4. Move on.

No codebase exploration, no design-it-twice, no ambiguity checks during
the copy task itself. Setup drift — historically ~20% of initial project
bugs — is eliminated by refusing to think about choices that were
already made.

### Phase 1.5: Pre-execution clarification (codebase-aware)

**This is NOT a re-validation of the plan.** `/validate-plan` (Phase 0b)
has already passed — the plan's structure, acceptance criteria, and
closed decisions are fine. Phase 1.5 is a separate, codebase-aware gate
that fires only when the plan, *read against the actual repo state*,
has more than one reasonable execution. It cannot run until the repo is
present, which is why it happens here and not inside `/validate-plan`.

When Phase 1.5 pauses, surface it with this framing so the operator
does not read it as "the plan is bad":

```
Plan validation: PASS (Phase 0b).
Pre-execution clarification needed:
  <N> point(s) in the plan map to more than one thing in this codebase.
  The plan itself is fine — I need you to pick a referent before I
  start coding, so I don't silently guess wrong.
```

Never phrase Phase 1.5 output as "the plan tasks are not atomic" or
"the plan has problems" — that contradicts the verdict that just passed
and is the single biggest UX defect this flow has shipped.

The executor must distinguish **ambiguity** (→ pause or abort) from
**uncertainty** (→ try). An ambiguity is a point where the plan has
more than one reasonable reading *given the repo* and picking silently
would produce code that might not match the author's intent. The
heuristic:

> Would a human reading the plan and seeing what I'm about to do say
> *"yes, that's obviously what I meant"*? If yes, proceed. If no, pause.

#### Three categories that count as ambiguity

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

#### What is NOT ambiguity (proceed, do not pause)

- *"I don't know how to implement this."* That's an executor-skill
  issue; try.
- *"There's a better way than the plan specifies."* That's scope
  discipline; follow the plan, log a `minor` finding.
- General uncertainty about outcomes — not the same as the plan having
  multiple reasonable readings.

#### Behaviour by mode

Governed by the `--interactive=<yes|no|auto>` argument (default `auto`):

| Mode | TTY? | Behaviour on ambiguity |
|---|---|---|
| `yes` | — | Pause, print the question, read a one-line answer. Record as `Clarification: <question>: <answer>` in the commit trailer. |
| `no` | — | Abort cleanly. Log the question in the final report's `## Open Questions` section. Resume (Task 3 of the hardening plan, when landed) can continue once the plan is updated. |
| `auto` | yes | Behave as `yes`. |
| `auto` | no | Behave as `no`. |

Record every ambiguity — answered or aborted — as a `plan-ambiguity`
finding in the final report.

### Phase 2: Per-Task Loop

For each task in order:

#### 2a. Read requirements
Read the task description. Understand what files to create/modify and what
behavior is expected.

#### 2b. Implement
Follow the plan exactly. Do not add unplanned features, refactors, or
"improvements."

#### 2c. Build
Run the `build` command from the repo-delivery schema (see
`_rubrics/repo-delivery` — the `## Commands` section of the repo's
`CLAUDE.md` is the only source).
- If build fails: diagnose, fix, retry (max 3 attempts).
- If still failing: stop and report.

#### 2d. Test — task's verifiable acceptance is the done-signal

The task's `verify:` frontmatter or Acceptance block (validated to be
mechanical per `validate-plan` check #4) IS the definition of "done"
for this task. Treat it as TDD:

1. If the criterion names a test that doesn't yet exist, **write the
   test first** (failing) before any implementation change. This proves
   the test exercises the expected behaviour.
2. Implement until every bullet in the acceptance block passes (each
   test exits 0, each `grep`/`test` one-liner exits 0, each observable
   reaches its stated value).
3. Then run the repo's full `test` command from the repo-delivery
   schema. Framework- and language-level tests must also pass; the
   task-level criterion is the *primary* gate but not the *only* gate.

- If task-level acceptance fails: diagnose, fix, retry (max 3 attempts).
- If the framework `test` command fails: diagnose, fix, retry (max 3 attempts).
- If still failing: stop and report.

#### 2e. Commit
Create a commit referencing the plan task. Task commits use the
standard `<type>(<scope>)` conventional form with a trailing
**Task footer**:

```
<type>(<scope>): <description>

<optional body>

Task N from <plan-file>
Plan-SHA: <sha>
Base-SHA: <sha>
```

The `Task N from <plan-file>` footer is reserved for this commit
class. Auto-fix commits (Phase 2.5 / 3b) never use it — they use a
distinct template (see "Auto-fix commits" below) so task progress and
review-fix progress are unambiguously distinguishable.

#### Auto-fix commits (Phase 2.5 / Phase 3b)

When a review phase's auto-fix cycle produces a code change, commit it
separately from the task work using this template:

```
review(<profile>): fix <finding-id> — <short summary>

Milestone-K or PR-boundary review auto-fix.
Plan-SHA: <sha>
Finding: <file>:<line> — <severity> <domain>
```

`<profile>` is `breakpoint` for Phase 2.5, `full` for Phase 3b. The
commit subject's `review(` prefix is the grep-able discriminator
between auto-fix work and task work.

**Never** include the `Task N from <plan-file>` footer in an auto-fix
commit — that footer is the marker `--resume` uses to count completed
tasks (see "Resume semantics"). Auto-fix commits may appear between
task commits; they must not be counted as task progress.

Commit after each successful auto-fix cycle, not batched per phase.
A finding that required three fix cycles before passing review
produces three `review(...)` commits, each referencing the same
`<finding-id>` but with a different subject summary.

#### 2f. Milestone check
If this task completes a milestone, proceed to Phase 2.5 before moving on.
Otherwise, continue to the next task.

#### 2g. Report
```
Task N/M: DONE — <brief summary>
  Files: <list>
  Commit: <sha>
```

If a task fails after retries:
```
Task N/M: BLOCKED — <failure description>
```
Stop execution.

### Phase 2.5: Breakpoint Review (at each milestone)

Invoke the `code-review` skill with `profile: breakpoint` against the diff
accumulated since the last milestone (or since `$EXECUTE_PLAN_BASE_SHA`
for the first milestone).

```
Milestone K/M: <name> — running breakpoint review
```

For each finding, assign a disposition status from the vocabulary in
`_rubrics/disposition/SKILL.md`:

- **critical / major**: auto-fix, then rebuild, retest, re-review.
  Max 3 cycles per finding. On success, set status → `fixed`.
  After 3 cycles without resolution, set status → `open` (blocks the
  verdict unless the operator supplies `--accept-risk=<id>`, which
  sets status → `accepted-risk` with audit logging).
- **minor / nit**: status → `open` by default; record for the
  PR-level report, do not auto-fix.
- **plan-ambiguity** / **plan-deviation**: not auto-fixed; handled per
  Phase 1.5 (ambiguity) / Phase 3d (deviation). The operator
  dispositions these explicitly as `disagree-with-evidence`, `defer`,
  or `accepted-risk`.

If any `critical` or `major` finding remains with status `open` after
the auto-fix attempts (and no `--accept-risk` was supplied), halt
milestone progress and surface the findings. Otherwise, resume the
per-task loop.

Every finding carries exactly one status end-of-phase. `open` is not a
valid end-state at Phase 4 — it must have been resolved (`fixed`),
disputed (`disagree-with-evidence`), deferred (`defer`), or accepted
(`accepted-risk`) by the end of the run.

### Phase 3: PR Boundary Reviews

After all tasks and milestones are complete, run the PR-level review stack.
This always runs at the PR boundary regardless of how many milestones fired.

#### 3a. Checkpoint
Invoke `/checkpoint` (lint, build, test) as the final quality gate. If it
fails, stop and report.

#### Phase 3 preamble: compute the effective diff + shared manifest

**Effective diff (exclusions).** Before triage or review dispatch,
compute the *effective* diff by excluding two path patterns from the
raw `git diff $EXECUTE_PLAN_BASE_SHA..HEAD`:

1. **The plan file itself.** If `/execute-plan` marked tasks as done
   in the plan during the run (or the plan was otherwise edited),
   those changes must not appear as review-scoped diff hunks — they
   are execution bookkeeping, not product code.
2. **`docs/decisions/<plan-slug>/` tree.** Decision records written
   this run (Task 14) are meta-artefacts about the execution. They
   explain choices; reviewers should not be asked to review them as
   if they were product code.

The effective diff is what `/checkpoint`, `/code-review`,
`/code-review-professional`, and `/review-adversarial` operate on.

Phase 3d (Plan alignment check) still reads the original plan
**directly from the plan file** — not from the effective diff — so
task-list reconciliation works regardless of in-run plan edits.

**Shared manifest.** Produce a single `diff_manifest` describing the
effective diff (not the raw diff):

```json
{
  "base_sha": "<EXECUTE_PLAN_BASE_SHA>",
  "head_sha": "<git rev-parse HEAD>",
  "files": [
    {
      "path": "src/api/auth.ts",
      "language": "typescript",
      "lines_added": 42,
      "lines_removed": 7,
      "touches": ["public-surface", "persistence", "auth"]
    }
  ],
  "clusters": [
    { "id": "backend", "paths": ["src/api/**", "src/services/**"] },
    { "id": "ui",      "paths": ["src/web/**"] },
    { "id": "db",      "paths": ["migrations/**", "src/db/**"] }
  ],
  "languages": { "typescript": 7, "sql": 2, "markdown": 1 },
  "touches": {
    "persistence": true,
    "public_surface": true,
    "concurrency": false,
    "auth": true,
    "dependencies": false
  }
}
```

Pass the same manifest to both `code-review` (in 3b) and
`code-review-professional` (in 3c). Both skills accept a
`diff_manifest` input and, when provided, skip their own internal
clustering step — they use the clusters, languages, and `touches`
flags already computed.

This ensures the two skills agree on component boundaries, eliminates
redundant triage work, and makes their reports comparable
cluster-by-cluster.

When either skill is invoked **directly** (not via execute-plan),
`diff_manifest` is absent and each skill falls back to its own internal
triage — no behavioural change for external users.

##### Intent / `pr_description` synthesis

Three downstream review skills (`code-review`,
`code-review-professional`, `review-adversarial`) accept an optional
`pr_description` input. The Phase 3 preamble synthesises one and
passes it to all three, so reviewers have a consistent framing of
*what this change is trying to achieve*.

Source of truth, in precedence:

1. **Plan frontmatter `intent:` field** — if the plan's frontmatter
   carries an `intent:` string, use it verbatim. Plans authored by
   `/plan` will typically populate this.
2. **Synthesised from the plan** — otherwise, build the intent from:
   - the plan's H1 title,
   - the first non-blank paragraph of the plan body,
   - a one-line summary of completed tasks (`Completed tasks: 1–N out
     of M. Milestones: K.`).

The synthesised version is good enough for reviewer framing — they
review the code against the intent, not the intent itself (that's
`/prd-validate`'s job upstream).

Pass the resulting `pr_description` string identically to 3b, 3c, and
3e. The three reviewers don't need to reach consensus on intent;
that's already resolved.

#### 3b. Full code review
Invoke `code-review` with `profile: full` against the cumulative diff
(`git diff $EXECUTE_PLAN_BASE_SHA..HEAD`) **and the shared
`diff_manifest`** from the Phase 3 preamble.

For each finding, assign a disposition status per
`_rubrics/disposition/SKILL.md` (same vocabulary as Phase 2.5):

- **critical / major**: auto-fix → rebuild → retest → re-review
  (max 3 cycles). Success → `fixed`. Failure → `open`, unless
  `--accept-risk=<id>` was supplied, in which case → `accepted-risk`.
- **minor / nit**: status → `open`; record for report, no auto-fix.
- **plan-ambiguity / plan-deviation**: require explicit disposition
  (`disagree-with-evidence` / `defer` / `accepted-risk`); never
  auto-fixed.

Same end-state rule as Phase 2.5: `open` is invalid at Phase 4. Every
finding ends the run with exactly one terminal status.

#### 3c. Professional review (craft grading)
Invoke `code-review-professional` against the cumulative diff **and the
shared `diff_manifest` from the Phase 3 preamble.** The skill uses the
manifest's `clusters` as its component boundaries — this guarantees
3b and 3c report on the same components.

Collect the per-component grades and overall read. Do not auto-fix
from the professional review — it's a judgment, not a defect list.
Grades go straight to the report.

#### 3d. Plan alignment check
1. Re-read the original plan.
2. Compare against the cumulative diff.
3. Verify: all tasks implemented, implementation matches spec, no
   unplanned additions.
4. Record gaps as **`plan-deviation`** findings (not `major`) — see
   `code-review/references/controller-guide.md` for the severity definition. Plan-deviations
   are not auto-fixed; each requires a terminal disposition.

Why `plan-deviation` and not `major`: unplanned changes are often
legitimate (a dep-patch-bump to unblock the build, a formatter
reformat). Treating them as `major` blocks every run; treating them
as `plan-deviation` with a disposition vocabulary lets the operator
separate real scope creep from mechanical necessity.

##### Auto-accept vs halt — disposition rules

**Process all deviations before halting.** Evaluate every deviation
against the rules below and record its outcome (disposition + rationale,
or "unmatched — would halt"). Only after every deviation has been
evaluated do you decide the overall run's fate: if any deviation is
unmatched in autonomous mode, halt. This way the operator sees the
complete deviation list in the abort report — not just the first one —
and can resume with a single set of `--accept-risk` flags rather than
paying an abort cycle per deviation.

For each deviation, apply these rules in order:

1. **`--accept-risk=<id>` supplied for this finding** → status
   `accepted-risk`. Record rationale (the operator's intent) in the
   report. Always available — works in interactive and autonomous
   modes.

2. **The deviation matches a category in `auto_accept_deviations`**
   (read from the repo-delivery schema; defaults
   `[lockfile, dep-patch-bump, formatter]`):
   - Auto-disposition as `disagree-with-evidence` with rationale
     `category: <matched-category>`.
   - Write a decision record (Task 14) under
     `docs/decisions/<plan-slug>/` so the auto-disposition is
     auditable. The record's `Context` cites the category; the
     `Reasoning` is the category rule; `Rejected alternatives` is empty
     by construction (there was no choice).
   - Proceed.

3. **No rule matches** and `--interactive=no` (autonomous/batch):
   **halt** via the Phase 0c failure path. The operator resumes by
   re-running with `--accept-risk=<id>` or by editing the plan to
   include the deviation as a planned change.

4. **No rule matches** and `--interactive=yes` (TTY): pause and ask
   the operator: *"Plan-deviation <id>: <summary>. Accept, defer, or
   dispute? (a/d/p)"*. Record the answer as the disposition and the
   operator's one-line rationale in a commit trailer.

##### Category definitions

These are the canonical definitions the executor applies when
matching against `auto_accept_deviations`:

- **lockfile** — changes only to
  `package-lock.json` / `pnpm-lock.yaml` / `yarn.lock` / `Cargo.lock` /
  `go.sum` / `poetry.lock` / `Pipfile.lock` / equivalent. A diff
  touching *only* these files (plus its manifest counterpart when the
  manifest change is itself `dep-patch-bump`) qualifies.

- **dep-patch-bump** — changes to a dependency's version string in
  `package.json` / `Cargo.toml` / `pyproject.toml` / `go.mod` /
  equivalent, where both the major and minor components are unchanged
  and only the patch component changed (semver `x.y.Z` → `x.y.Z'`).
  Major or minor bumps do **not** qualify.

- **formatter** — changes that alter only whitespace, newlines, or
  quote style with no AST-level semantic difference. If you're unsure
  whether a change is semantic, it does NOT qualify. When in doubt,
  halt.

- **auto-generated-files** — changes entirely within paths matching
  `auto_generated_paths` from the repo-delivery schema. Requires the
  repo to have opted in by declaring the paths.

Each plan-deviation gets its own row in the findings table. The
`## Plan Deviations` section in the final report groups them for
audit visibility. Dispositioned deviations count as WARN; `open`
deviations count as FAIL.

#### 3e. Adversarial review (flag-driven)

Governed by the `--adversarial=<auto|always|never|ask>` argument (see
Arguments). Default is `auto`.

Decision table:

| Flag value | Behaviour |
|---|---|
| `auto` (default) | Fire if diff ≥200 lines OR diff touches an `adversarial_triggers` path. Otherwise skip silently. |
| `always` | Fire unconditionally. |
| `never` | Skip. No prompt, no invocation. |
| `ask` | Prompt the user interactively (legacy behaviour — only when a human is supervising). |

When firing, invoke `/review-adversarial` against the cumulative diff,
passing the shared `pr_description` from the Phase 3 preamble as its
`intent` input so reviewers frame their adversarial challenge against
the same stated goal as 3b/3c. Append its output to the final report.

When skipping under `auto`, record the reason (`diff below threshold`,
`no trigger paths touched`) in the report so the decision is auditable.

### Phase 4: Final Report

Write **two** artefacts at the end of the run:

- `execution-report.md` — human-facing markdown report (see format below).
- `execution-report.json` — structured counterpart for CI and
  downstream tooling.

Paths are configurable via `--report-path=<dir>`; default is the
current working directory. Both files always land together — never
one without the other.

#### JSON schema

```json
{
  "verdict": "PASS",
  "plan_file": "docs/plans/<plan-slug>.md",
  "plan_sha": "<plan file sha at Phase 0c>",
  "base_sha": "<EXECUTE_PLAN_BASE_SHA>",
  "head_sha": "<git rev-parse HEAD>",
  "branch": "<branch name>",
  "mode": "auto | yes | no",
  "tasks": [
    {
      "id": 1,
      "description": "...",
      "status": "DONE | BLOCKED",
      "commit": "<sha>",
      "files": ["..."]
    }
  ],
  "milestones": [
    {
      "id": 1,
      "name": "...",
      "breakpoint_review": {
        "findings": [ { "id": "F-001", "severity": "...", "status": "..." } ]
      }
    }
  ],
  "findings": [
    {
      "id": "F-001",
      "severity": "critical | major | minor | nit | plan-ambiguity | plan-deviation",
      "file": "path/to/file",
      "line": 42,
      "summary": "...",
      "status": "open | fixed | disagree-with-evidence | defer | accepted-risk | resolved",
      "rationale": "..."
    }
  ],
  "grades": {
    "components": [
      { "name": "backend", "grade": "senior", "axes": { "clarity": "senior", "...": "..." } }
    ],
    "overall_read": "..."
  },
  "retry_stats": {
    "total_retries": 0,
    "wall_clock_minutes": 0,
    "budget_used_fraction": 0.0
  },
  "adversarial": {
    "status": "ran | skipped | failed",
    "reason": "...",
    "verdict": "PASS | CONTESTED | REJECT | null",
    "findings": []
  },
  "open_questions": [
    { "task": 3, "question": "...", "raised_at_phase": "1.5" }
  ],
  "decisions_written": [
    { "id": "20260419-0042", "path": "docs/decisions/<plan-slug>/0042-...md", "tags": ["..."], "files": ["..."] }
  ]
}
```

Rules:
- `verdict` uses the same vocabulary as the markdown verdict line
  (`PASS` / `WARN` / `FAIL`).
- `open_questions` is populated only when batch mode aborts on
  ambiguity (Phase 1.5 `--interactive=no` path).
- `decisions_written` lists every record produced this run; empty
  array if none qualified under the filter rule.
- `adversarial.status` is `skipped` in `auto` mode when no CLI or
  thresholds not met; `ran` when invoked; `failed` only when explicit
  invocation (`--adversarial=always` or direct) couldn't proceed.
- `findings` consolidates across Phase 2.5 breakpoint and Phase 3b
  full review; each has a unique `id`.

#### Markdown report

```
## Execution Report

**Plan:** <plan-file>
**Tasks:** N/N completed across M milestones

### Per-Task Summary
| # | Description | Commit | Files | Status |
|---|---|---|---|---|
| 1 | ... | abc1234 | 3 | DONE |

### Breakpoint Reviews

Each row shows counts by severity, with disposition statuses
(`fixed / open / disagree-with-evidence / defer / accepted-risk`)
broken out. See `_rubrics/disposition/SKILL.md` for the vocabulary.

| Milestone | Severity | Count | Status breakdown |
|---|---|---|---|
| 1: <name> | Critical | 0 | — |
| 1: <name> | Major | 1 | fixed: 1 |
| 1: <name> | Minor | 2 | open: 2 |

### PR Reviews

**Full code review (profile: full):**

| Severity | Count | Status breakdown |
|---|---|---|
| Critical | N | fixed: N · accepted-risk: N · open: N |
| Major | N | fixed: N · accepted-risk: N |
| Minor | N | open: N · defer: N |
| Nits | N | open: N |
| plan-ambiguity | N | disagree-with-evidence: N · defer: N |
| plan-deviation | N | accepted-risk: N · disagree-with-evidence: N |

**Findings table (full detail):**

| ID | Severity | File:Line | Summary | Status |
|---|---|---|---|---|
| F-001 | major | src/foo.ts:42 | ... | fixed |
| F-002 | minor | src/bar.ts:17 | ... | open |

**Professional review (craft grading):**
| Component | Grade | Notes |
|---|---|---|
| Backend (src/api/, src/services/) | senior | ... |
| UI (src/web/) | junior | ... |

Overall read: <one paragraph>

**Plan alignment:**
- All tasks implemented: YES/NO
- Unplanned changes: NONE / [list]

### Plan Deviations

Dedicated section for `plan-deviation` findings from Phase 3d. Each
must have a terminal disposition; `open` is invalid at Phase 4.

| ID | File:Line | Summary | Disposition | Rationale |
|---|---|---|---|---|
| D-001 | package.json:15 | Bumped `drizzle-orm` to unblock build | disagree-with-evidence | Plan Task 3 says "use Drizzle"; version bump was implicit. |
| D-002 | src/utils/date.ts (new) | Extracted `formatAge` helper | defer | Not in plan; tracked as follow-up #142. |

**Plan Ambiguities** (from Phase 1.5 / validate-plan):

Same structure — ambiguities that surfaced during execution, each with
its resolution recorded in a commit trailer (`Clarification: ...`)
or, in batch mode, as an open question the operator must close before
re-running.

**Adversarial review:** [summary if run, or "declined"]

### Checkpoint
- Lint: PASS/FAIL
- Build: PASS/FAIL
- Tests: PASS/FAIL

### Verdict: PASS / WARN / FAIL

[If PASS]: Ready to ship.
[If WARN]: Review minor findings before shipping.
[If FAIL]: Fix listed issues before shipping.
```

Verdict rules (apply the disposition rubric in
`_rubrics/disposition/SKILL.md`; `open` is not a valid end-state):

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

## Key Rules

- **Validate before executing.** Phase 0 is not optional.
- **Follow the plan exactly.** No unplanned features, refactors, or "improvements."
- **Stop on persistent failure.** After 3 retries, stop and report rather than spiraling.
- **Breakpoint reviews are light; PR reviews are thorough.** Breakpoint uses `profile: breakpoint` (security/correctness/tests). PR uses `profile: full` (all 11 domains) plus the professional grade.
- **Adversarial review is flag-driven.** Governed by `--adversarial` (default `auto`). Autonomous runs never pause to ask; interactive supervisors can opt in with `--adversarial=ask`.
- **Commits reference the plan.** Every commit ties back to a task number. Commit trailers carry `Plan-SHA` and `Base-SHA` so the run is fully reconstructable.
- **Never destroy work on failure.** Abort preserves the branch and tags the last good commit as `execute-plan/abort/...`. Destructive git ops (`reset --hard`, `push --force`, `branch -D`, `clean -f`) are forbidden in all code paths.
