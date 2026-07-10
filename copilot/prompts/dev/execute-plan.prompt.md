---
description: >-
  Execute an accepted implementation plan with full staged governance: plan
  validation gate, codebase-aware ambiguity handling, optional parallel agent
  lanes, per-task TDD build/test cycles, milestone breakpoint reviews, diff
  manifest scoped dispatch, PR-boundary code review + professional review, and
  auto-fired postmortem on WARN/FAIL.
argument-hint: '[path/to/plan.md] [--interactive=yes|no|auto] [--force] [--resume] [--create-branch] [--accept-risk=id] [--adversarial=auto|always|never] [--run-folder=auto|off|path] [--max-retries=N] [--max-minutes=N] [--postmortem=auto|always|never] [--postmortem-mode=auto|full|lightweight]'
agent: 'agent'
tools:
  - execute
  - read
  - search
  - edit
  - codebase
---

# Execute Plan

Use this prompt after a plan is already approved and ready to implement.

Follow the skills:

- `.github/skills/repo-delivery/SKILL.md`
- `.github/skills/execution-environment/SKILL.md`
- `.github/skills/parallel-optimization/SKILL.md` (when the plan declares `## Parallel Execution`)
- `.github/skills/test-planning/SKILL.md` (for per-task TDD cycles)
- `.github/skills/review-engine/SKILL.md` (for breakpoint and PR-boundary reviews)
- `.github/skills/review-disposition-governance/SKILL.md` (finding disposition vocabulary)

## When to Use

- You have a written plan file ready to execute.
- You want per-task build/test cycles plus staged code reviews.
- You want a seniority-calibrated craft grade on the final output.

## When NOT to Use

- No plan exists yet — use the built-in `/plan` first.
- Trivial single-file change — make the edit directly.

## Arguments

| Argument | Description |
|---|---|
| `<path>` | Path to the plan file. If omitted, uses the most recent `.md` in `docs/plans/`. |
| `--interactive=yes\|no\|auto` | How to handle execution-time ambiguity. `yes` = pause and ask on every ambiguity. `no` = batch mode; never prompt; log ambiguities in the final report's `## Open Questions`. `auto` (default) = detect TTY and behave accordingly. |
| `--force` | Bypass the refuse-on-FAIL contract (Phase 0b). Plan validation returning FAIL still runs anyway. **For humans only — never set by automation.** Use is logged prominently in the execution report. |
| `--resume` | Resume a previously aborted run. Scans commits on the current branch for `Task N from <plan-file>` footers; verifies all prior task commits share the same `Plan-SHA`; re-runs the last milestone's breakpoint review, then proceeds at the next task. |
| `--create-branch` | Create a feature branch even if HEAD is already on a non-default branch. Branch named `execute-plan/<plan-slug>-<YYYYMMDD-HHMM>` off the default branch. |
| `--accept-risk=<finding-id>` | Explicitly accept a critical or major finding. Repeatable. Human-only override; record every use in the final report. |
| `--adversarial=auto\|always\|never` | When to run adversarial review (Phase 3e). `auto` (default) = fires when cumulative diff ≥ 200 lines or touches a security-sensitive path. `always` = unconditional. `never` = skip. |
| `--run-folder=<auto\|off\|path>` | Where to write run artefacts such as `execution-report.md`, `execution-report.json`, `disposition-log.md`, and optional `postmortem.md`. Default: `auto` (use repo-configured `runs_root` when declared; otherwise current working directory). |
| `--max-retries=N` | Override the global retry budget (default: 20). |
| `--max-minutes=N` | Override the wall-clock budget (default: 60). |
| `--postmortem=auto\|always\|never` | When to run Phase 5 postmortem. `auto` (default) = fires on WARN, FAIL, retry-budget exhaustion, or unproved coverage. |
| `--postmortem-mode=<auto\|full\|lightweight>` | How deep the Phase 5 postmortem goes. `auto` chooses `lightweight` for fragile PASS cases and `full` for WARN/FAIL/blocked runs. |

## Workflow

### Phase 0: Preflight

Three gates run before any execution work.

**0a. Repo-delivery contract.** Read the `## Commands` section of `copilot-instructions.md`
per `.github/skills/repo-delivery/SKILL.md`. If it is missing, fail fast:

```
Repo missing required copilot-instructions.md ## Commands section.
See .github/skills/repo-delivery/SKILL.md for the schema.
```

The `lint` / `build` / `test` / `default_branch` / `package_manager` fields drive
every subsequent phase.

**0b. Validate plan — refuse contract.** Read the plan and apply the validate-plan
checklist below. If the verdict is `FAIL`, refuse to execute and surface the findings.
Do not proceed except with explicit `--force`. This is non-negotiable.

#### Validate-plan checklist (inline)

Apply all ten checks. Emit `VERDICT: PASS` or `VERDICT: FAIL` with a findings table.

| # | Check | Fail condition |
|---|---|---|
| 1 | Frontmatter present | `slug`, `title`, or `version` missing |
| 2 | Tasks are ordered and numbered | Missing numbering or circular dependencies |
| 3 | Each task has a scope | No files or components listed for a task |
| 4 | Each task has mechanical acceptance criteria | Acceptance is prose-only with no verifiable signal (test, grep, build exit code) |
| 5 | No task has unbounded scope | Task description spans more than one distinct behaviour unit |
| 6 | Milestones are declared | No `## Milestone:` markers and no `milestones:` frontmatter list |
| 7 | Default branch named | `default_branch` absent from plan or repo-delivery schema |
| 8 | Dependencies are resolved | A task lists a dependency not defined in the plan |
| 9 | Closed decisions are consistent | A closed decision contradicts another in the same plan |
| 10 | Parallel Execution section is well-formed (when present) | Lane ownership overlaps, missing barriers, or ≥5 lanes in one wave |

The `--force` escape hatch records the bypass prominently:

```
WARNING — plan validation FAILED and was overridden with --force.
Outstanding findings from validate-plan:
  - [check N] ...
```

**0b.5. Tool-availability probe.** Verify every command declared in `copilot-instructions.md`
`## Commands` resolves on PATH. Subagent shells do not inherit interactive shell profiles,
so toolchains managed by `nvm`, `fnm`, `pyenv`, `asdf`, or similar must be visible before
any subagent spawns.

Probe explicitly:

```bash
command -v "<package_manager>"
command -v "<lint_cmd first token>"
command -v "<build_cmd first token>"
command -v "<test_cmd first token>"
# JavaScript / TypeScript repos:
command -v node
```

If any probe fails, halt with a message naming the missing tools, the likely
cause (version manager not on PATH), and three remediation options:
1. Activate the toolchain version before re-invoking.
2. Add the absolute toolchain path to `copilot-instructions.md ## Commands`.
3. Install the tool system-wide.

When probes pass, confirm: `Toolchain probe OK: <pm> <pm-version>, <test-runner>.`

Any worker or agent shell launched after this probe must use the same
environment-routing strategy validated here. Do not assume a bare subshell will
inherit the right PATH or version-manager initialization.

**0c. Prepare workspace.** After 0a, 0b, and 0b.5 succeed:

1. Read `default_branch` from the repo-delivery schema.
2. Refuse to run on the default branch. If HEAD equals `default_branch`, halt:
   ```
   /execute-plan refuses to run directly on the default branch (`<branch>`).
   Create a feature branch, or pass --create-branch.
   ```
3. If `--create-branch`, create and switch to `execute-plan/<plan-slug>-<YYYYMMDD-HHMM>`.
4. Record `$EXECUTE_PLAN_BASE_SHA` (current commit). Every task commit carries
   `Base-SHA: <sha>` and `Plan-SHA: <plan-sha>` trailers.
5. Record the active branch name for failure-path preservation.

**Failure path — preserve, never destroy.** On any unrecoverable failure:
1. Tag the last successful commit as `execute-plan/abort/<plan-slug>-<YYYYMMDD-HHMM>`.
2. Leave the branch and index intact. Never stash, reset, or clean working-tree changes.
3. Surface: `Run aborted. Branch preserved at <branch>. Resume with: /execute-plan --resume <plan-file>`
4. Stop with a non-zero signal so CI can detect the abort.

Forbidden git operations in all code paths: `reset --hard`, `push --force`,
`branch -D`, `clean -f`, force-overwriting tags.

**Retry budget (global circuit breaker).** Defaults: 20 total retries, 60 wall-clock
minutes. Override via `--max-retries` / `--max-minutes` or via `retry_budget:` in
`copilot-instructions.md ## Commands`. The counter increments on every build retry,
test retry, and auto-fix cycle. When exhausted: tag + abort + resume instructions.

### Phase 1: Load Plan

1. If no path argument, find the most recent `.md` in `docs/plans/`.
2. Parse the plan into an ordered task list (numbered sections, headings, or checklist items).
3. Identify milestones from `## Milestone:` markers or a `milestones:` frontmatter list.
   If neither exists, treat every top-level `##` section boundary as an implicit milestone.
4. Report: `Found N tasks across M milestones in <plan-file>. Starting execution.`
5. Load closed decisions from any `## Closed Decisions` section. These are tablestakes:
   do not propose alternatives, do not surface them as ambiguity — execute as stated.
6. Load the parallel lane registry if a `## Parallel Execution` section is present
   (mode, ownership lanes, barriers, single-owner files). Reference
   `.github/skills/parallel-optimization/SKILL.md` for lane scheduling rules.
7. Load the wave registry from any `## Waves` section or `--- WAVE N START ---` markers.
   Waves compose with lanes: lanes describe which tasks fan out; waves describe when.

### Phase 1.1: Parallel lane readiness

When a lane registry exists:

1. Build a task-to-lane map from the `Ownership` table.
2. Reject `parallel` mode if two lanes may write the same file/glob without a single owner.
3. Reject `parallel` mode if a lane depends on an undefined task or barrier.
4. Refuse ≥5 parallel lanes in a single wave — coordination overhead dominates.
   In interactive mode ask the operator to fix the plan; in autonomous mode abort.
5. Report the chosen mode, lanes, barriers, and wave count.

### Phase 1.5: Pre-execution clarification (codebase-aware)

This is NOT re-validation of the plan. Phase 0b has already passed. This gate fires
only when the plan, read against the actual repo state, has more than one reasonable
execution path.

Surface it clearly so the operator does not read it as "the plan is bad":

```
Plan validation: PASS (Phase 0b).
Pre-execution clarification needed:
  <N> point(s) in the plan map to more than one thing in this codebase.
  The plan itself is fine — I need you to pick a referent before I
  start coding, so I don't silently guess wrong.
```

#### Three categories that count as ambiguity

1. **Referent ambiguity** — the plan names a thing and the repo has multiple candidates.
2. **Existing-state ambiguity** — the plan prescribes an addition and the repo already has
   something overlapping (add-on, replace, or stack are all defensible).
3. **Scope-boundary ambiguity** — the change's natural boundary crosses something the plan
   didn't mention.

#### What is NOT ambiguity (proceed, do not pause)

- "I don't know how to implement this." That's an executor-skill issue; try.
- "There's a better way than the plan specifies." Follow the plan, log a `minor` finding.
- General uncertainty about outcomes.

#### Behaviour by mode

| Mode | TTY? | Behaviour |
|---|---|---|
| `yes` | — | Pause, print the question, read a one-line answer. Record as `Clarification: <question>: <answer>` in the commit trailer. |
| `no` | — | Abort cleanly. Log the question in the final report `## Open Questions`. |
| `auto` | yes | Behave as `yes`. |
| `auto` | no | Behave as `no`. |

Record every ambiguity — answered or aborted — as a `plan-ambiguity` finding in the report.

### Phase 2: Per-Task Loop

For each task in order:

#### 2a. Read requirements

Read the task description. Identify what files to create or modify and what behaviour
is expected. Query `docs/decisions/index.json` for existing decision records that
govern any target file. Pass matching records to the implementation step with this
directive: *"These decisions govern files you're about to modify. Do not reverse a
non-superseded decision without raising a `plan-ambiguity` finding."*

#### 2b. Implement

Follow the plan exactly. No unplanned features, refactors, or "improvements."

If parallel lanes are active and the runtime permits it, dispatch currently unblocked
lanes whose write scopes are disjoint per the lane registry. Every worker context
must include:

> You are not alone in the codebase. Own only the assigned write scope, do not revert
> edits made by others, and adjust your implementation to accommodate changes from
> other lanes. If your task requires editing a file outside your write scope, stop and
> report the needed scope change.

For parallel wave dispatch mechanics (worktree preparation, single-message dispatch,
per-lane review and fix, model selection, sequential merge), follow the rules in
`.github/skills/parallel-optimization/SKILL.md`.

#### 2c. Build

Run the `build` command from `copilot-instructions.md ## Commands`.
- If build fails: diagnose, fix, retry (max 3 attempts).
- If still failing: stop and report.

#### 2d. Test — TDD cycle, task acceptance is the done-signal

Reference `.github/skills/test-planning/SKILL.md` for the test-first approach.

1. If the acceptance criterion names a test that doesn't yet exist, write the test
   first (failing) before any implementation change.
2. Implement until every bullet in the acceptance block passes.
3. Then run the full `test` command from the repo-delivery schema. Task-level
   acceptance is the primary gate but not the only gate.

- If acceptance fails: diagnose, fix, retry (max 3 attempts).
- If still failing: stop and report.

#### 2e. Commit

Task commits use conventional commit form with a trailing Task footer:

```
<type>(<scope>): <description>

Task N from <plan-file>
Plan-SHA: <sha>
Base-SHA: <sha>
```

Auto-fix commits (from Phase 2.5 / Phase 3b cycles) use a distinct template — never
include the `Task N` footer. The `review(` subject prefix is the discriminator:

```
review(<profile>): fix <finding-id> — <short summary>

Plan-SHA: <sha>
Finding: <file>:<line> — <severity> <domain>
```

Commit after each successful auto-fix cycle, not batched per phase.

#### 2f. Milestone check

If this task completes a milestone, run Phase 2.5 before moving on.
If this task is the last in a wave, enforce the wave barrier check:
re-run full build and test even if no milestone fell here, and
re-validate lane ownership before dispatching the next wave.

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

Use `prompts/review/domain-review.prompt.md` with `profile: breakpoint` against the diff
accumulated since the last milestone (or since `$EXECUTE_PLAN_BASE_SHA` for the first
milestone).

```
Milestone K/M: <name> — running breakpoint review
```

Apply disposition vocabulary from `.github/skills/review-disposition-governance/SKILL.md`:

- **critical / major**: auto-fix → rebuild → retest → re-review. Max 3 cycles per finding.
  On success → `fixed`. After 3 cycles without resolution → `open` (blocks verdict unless
  `--accept-risk=<id>` was supplied → `accepted-risk` with audit logging).
- **minor / nit**: status → `open`; record for the PR-level report, no auto-fix.
- **plan-ambiguity / plan-deviation**: not auto-fixed; handled per Phase 1.5 / Phase 3d.

If any `critical` or `major` finding remains `open` after auto-fix attempts with no
`--accept-risk`, halt milestone progress and surface the findings. Every finding must
have a terminal status by Phase 4 — `open` is not valid at end-of-run.

### Phase 3: PR Boundary Reviews

After all tasks and milestones are complete, run the PR-level review stack.

#### 3a. Checkpoint

Run `prompts/dev/checkpoint.prompt.md` (lint, build, test) as the final quality gate.
If it fails, stop and report.

#### Phase 3 preamble: diff manifest and intent synthesis

**Effective diff (exclusions).** Compute the effective diff by excluding:
1. The plan file itself (execution bookkeeping, not product code).
2. `docs/decisions/<plan-slug>/` (meta-artefacts about the execution).

The effective diff is what all Phase 3 reviews operate on.

**Diff manifest.** Produce a single `diff_manifest` describing the effective diff:

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

Pass the same manifest to both `domain-review` (3b) and `professional-review` (3c)
so they use the same component clusters and skip redundant triage work.

**Intent synthesis.** Synthesise a `pr_description` from the plan's `intent:` frontmatter
field if present, otherwise from the plan's H1 title + first paragraph + a one-line task
summary. Pass it identically to 3b, 3c, and 3e so all reviewers frame against the same
stated goal.

#### 3b. Full code review

Use `prompts/review/domain-review.prompt.md` with `profile: full` against the cumulative
diff, passing the shared `diff_manifest` and `pr_description`.

Apply the same disposition vocabulary as Phase 2.5:
- **critical / major**: auto-fix → rebuild → retest → re-review (max 3 cycles).
- **minor / nit**: status → `open`; record for report.
- **plan-ambiguity / plan-deviation**: require explicit disposition; never auto-fixed.

`open` is not a valid end-state at Phase 4. Every finding ends with exactly one
terminal status.

#### 3c. Professional review (craft grading)

Use `prompts/review/code-review-professional.prompt.md` against the cumulative diff,
passing the shared `diff_manifest`. The manifest's `clusters` serve as component
boundaries, ensuring 3b and 3c report on the same components.

Collect per-component grades and the overall read. Do not auto-fix from the professional
review — it is a judgment, not a defect list. Grades go straight to the report.

#### 3d. Plan alignment check

1. Re-read the original plan.
2. Compare against the cumulative diff.
3. Verify: all tasks implemented, implementation matches spec, no unplanned additions.
4. Record gaps as `plan-deviation` findings — not `major` severity. Plan-deviations
   require a terminal disposition but are never auto-fixed.

**Auto-accept categories.** Deviations matching these categories are dispositioned
`disagree-with-evidence` automatically (configurable via `auto_accept_deviations` in
`copilot-instructions.md ## Commands`; defaults: `lockfile`, `dep-patch-bump`,
`formatter`, `auto-generated-files`):
- **lockfile** — changes only to lock files (`package-lock.json`, `pnpm-lock.yaml`, etc.)
- **dep-patch-bump** — patch-only version bumps in manifest files
- **formatter** — whitespace/quote-style only, no AST-level semantic difference
- **auto-generated-files** — changes within paths declared as `auto_generated_paths`

Process all deviations before halting — the operator sees the complete list in the abort
report and can resume with a single set of `--accept-risk` flags.

**Proof accounting.** For each completed task, classify every acceptance criterion:
- `proved` — a test in the diff exercises the behaviour AND passed in Phase 3a.
- `partially-proved` — some coverage exists but at least one bullet is unverified.
- `unproved` — no test exercises the behaviour; criterion was satisfied by inspection only.

Emit a proof-accounting table in the report. Any `unproved` row triggers the postmortem
(Phase 5) and is noted in the WARN summary line.

#### 3e. Adversarial review (flag-driven)

Governed by `--adversarial` (default `auto`).

| Flag value | Behaviour |
|---|---|
| `auto` | Fire if diff ≥200 lines or diff touches a security-sensitive path configured in `copilot-instructions.md` (`adversarial_triggers`). Otherwise skip silently and record the reason. |
| `always` | Fire unconditionally. |
| `never` | Skip. No prompt, no invocation. |

When firing, use `prompts/review/review-adversarial.prompt.md` against the cumulative
diff, passing `pr_description` as the intent input. Append its output to the final report.

Default `adversarial_triggers` paths (override in `copilot-instructions.md ## Commands`):
```
adversarial_triggers:
  - src/auth/**
  - src/payments/**
  - migrations/**
  - **/crypto/**
```

### Phase 4: Final Report

Write two run artefacts at the project's `runs_root` path (declared in
`copilot-instructions.md ## Commands`) or at the current working directory if not set.

**`execution-report.md`** (human-facing):

```
## Execution Report

**Plan:** <plan-file>
**Tasks:** N/N completed across M milestones

### Per-Task Summary
| # | Description | Commit | Files | Status |
|---|---|---|---|---|

### Breakpoint Reviews
| Milestone | Severity | Count | Status breakdown |
|---|---|---|---|

### PR Reviews

**Full code review (profile: full):**
| Severity | Count | Status breakdown |
|---|---|---|

**Findings table:**
| ID | Severity | File:Line | Summary | Status |
|---|---|---|---|---|

**Professional review (craft grading):**
| Component | Grade | Notes |
|---|---|---|

Overall read: <one paragraph>

**Plan alignment:**
- All tasks implemented: YES/NO
- Unplanned changes: NONE / [list]

**Proof accounting:**
| Task | Acceptance criterion | Classification | Evidence |
|---|---|---|---|

### Plan Deviations
| ID | File:Line | Summary | Disposition | Rationale |
|---|---|---|---|---|

**Adversarial review:** [summary if run, or reason skipped]

### Checkpoint
- Lint: PASS/FAIL
- Build: PASS/FAIL
- Tests: PASS/FAIL

### Verdict: PASS / WARN / FAIL
```

**`execution-report.json`** (structured, for CI and downstream tooling). Fields include
`verdict`, `gate_state`, `plan_file`, `plan_sha`, `base_sha`, `head_sha`, `branch`,
`mode`, `tasks`, `milestones`, `findings`, `grades`, `retry_stats`, `adversarial`,
`open_questions`, `decisions_written`, and `proof_accounting`.

**Gate state vocabulary** (four states for CI routing; `verdict` is for humans):

| `gate_state` | Meaning | Maps to |
|---|---|---|
| `completed` | All findings terminally dispositioned, no accepted risk | PASS |
| `completed-with-accepted-risk` | One or more `accepted-risk` dispositions | PASS or WARN |
| `blocked` | Retry budget hit or `open` critical/major after auto-fix exhaustion | FAIL |
| `awaiting-human-decision` | A finding requires explicit human arbitration | FAIL |

**Verdict rules:**

- **PASS** — all tasks done; every critical/major is `fixed` or `accepted-risk`; only
  minor/nit/plan-deviation/plan-ambiguity findings remain in terminal status; checkpoint
  passes; plan aligned.
- **WARN** — all tasks done; some minor/nit findings in terminal status; plan-deviations
  have terminal dispositions; no blocking criticals/majors; checkpoint passes.
- **FAIL** — any critical/major ends `open`; any plan-deviation or plan-ambiguity ends
  `open`; checkpoint fails; or plan alignment has undispositioned gaps.

The professional grade does not affect the verdict. A `junior`-graded component still
PASSes if it is bug-free.

### Phase 5: Postmortem

Governed by `--postmortem` (default `auto`) and `--postmortem-mode` (default `auto`).

**Auto trigger fires when any of the following is true:**
- final verdict is WARN or FAIL
- `gate_state` is `blocked` or `awaiting-human-decision`
- retry budget exhaustion was hit
- any `unproved` row exists in the proof-accounting table
- any auto-fix cycle required all 3 attempts
- any `plan-deviation` ended `accepted-risk`

**Mode resolution (`auto`):**
- `lightweight` — PASS with unproved rows or fragile auto-fix only. Sections: What happened, What broke down, Recommendations.
- `full` — WARN, FAIL, blocked, awaiting-human-decision, retry-budget exhaustion, accepted-risk plan-deviations.

When firing, use `prompts/dev/postmortem.prompt.md`, passing:
- `execution-report.md` and `.json`
- `disposition-log.md` (when present in the run folder)
- the original plan file
- the source requirements artefact, if known

Write `postmortem.md` to the run folder. After writing, append a row to
`docs/postmortems/index.json` (create as `[]` if absent). Then surface:

```
Postmortem: <run-folder>/postmortem.md  (mode: <mode>)
Key recommendation: <most actionable finding>
```

**Hard rules:**
- Not a second requirements document.
- Not a chat-transcript summary.
- Not a restatement of review findings.
- Target one page (full mode) or half a page (lightweight).

### Decision records

When execution makes a non-trivial design call the plan didn't prescribe, resolves a
`plan-ambiguity`, or dispositions a `plan-deviation`, write a decision record.

Store path: project-specific — see `copilot-instructions.md` for the
`decisions_root` path, or default to `docs/decisions/<plan-slug>/`. Each record uses
the format: one markdown file per decision with frontmatter (`id`, `plan`, `task`,
`date`, `files`, `tags`, `supersedes`, `superseded_by`) and body sections (Context,
Decision, Reasoning, Rejected alternatives, Consequences, Revisit if).

Maintain `docs/decisions/INDEX.md` (human-facing) and `docs/decisions/index.json`
(machine-queryable) updated on every write or supersede.

**Filter rule:** Write a record ONLY when a reasonable future agent, seeing only the
code, could plausibly reverse the choice. Forced, trivial, or fully-plan-prescribed
choices do not get records. More than 5 records in a single task is a noise signal.

**Read trigger:** At the start of each task's implementation (Phase 2a), query
`docs/decisions/index.json` for records whose `files` entries match the task's target
files. Pass matching records to the implementing worker.

## Copilot-native usage

- Use the built-in `/plan` first if the work is not already planned.
- Follow the plan literally unless the user explicitly authorizes a deviation.
- Stop cleanly on blockers instead of skipping ahead.
- Use `prompts/review/domain-review.prompt.md` for breakpoint and full reviews.
- Use `prompts/review/code-review-professional.prompt.md` for craft grading at the PR boundary.
- Use `prompts/review/review-adversarial.prompt.md` at the PR boundary when the adversarial trigger fires.
- Use `prompts/dev/postmortem.prompt.md` for Phase 5 postmortem invocation.
- Read `copilot-instructions.md` (not `CLAUDE.md`) for repo-specific configuration.

## Key Rules

- **Validate before executing.** Phase 0 is not optional. The inline validate-plan checklist runs before any implementation work.
- **Follow the plan exactly.** No unplanned features, refactors, or "improvements."
- **Stop on persistent failure.** After 3 retries, stop and report rather than spiraling.
- **Breakpoint reviews are light; PR reviews are thorough.** Breakpoint uses `profile: breakpoint` (security/correctness/tests). PR uses `profile: full` plus the professional grade.
- **Adversarial review is flag-driven.** Default `auto`. Autonomous runs never pause to ask.
- **Commits reference the plan.** Every task commit carries `Plan-SHA` and `Base-SHA` trailers. Auto-fix commits use a `review(` subject prefix — never a `Task N` footer.
- **Never destroy work on failure.** Abort preserves the branch and tags the last good commit. Destructive git ops are forbidden in all code paths.
- **Green tests are not proof.** Phase 3d emits a proof-accounting table classifying every acceptance bullet as `proved` / `partially-proved` / `unproved`.
- **Postmortems are for the next run, not this one.** Phase 5 fires automatically on WARN/FAIL/blocked/unproved coverage. It analyses process, not scope or findings, and is capped at one page.
- **Parallel waves run in isolation.** Per `.github/skills/parallel-optimization/SKILL.md`: isolated branches, single-message fan-out, sequential merge. Max 4 lanes per wave.
- **Never resume a prior subagent.** Each fixer pass is a fresh dispatch with findings and target files in its prompt.
