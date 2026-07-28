# claude-new Execute-PRD / Execute-Plan Rebuild Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the execute-prd → execute-plan pipeline in `claude-new/` with the orchestration mechanics compiled into a Workflow script, prohibitions enforced by permissions/hooks, commodity reviews delegated to built-ins, and only the judgment content kept as skill prose.

**Architecture:** Two-stage compile/execute split is preserved. `claude-new/execute-prd` (compiler) emits plans in a new structured format with explicit task dependencies; `claude-new/execute-plan` (thin judgment skill) runs preflight gates then drives `workflows/run-plan.mjs` — a Workflow script that owns the task loop, retry accounting, review-fix cycles, parallel lanes (worktree isolation), and report assembly in real code instead of prose. Destructive-git prohibitions move to `settings.template.json` deny rules. The old `claude/execute-prd` and `claude/execute-plan` are untouched; `claude-new/` is a parallel staging tree.

**Tech Stack:** Claude Code skills (SKILL.md), Workflow tool scripts (plain JS, ESM, no fs/Date access — agents do all I/O), JSON Schema for agent structured outputs, existing `claude/_internal/*` contracts (referenced, not copied).

## Global Constraints

- All new files live under `claude-new/` except the two `settings.template.json` deny-rule edits noted in Task 7 (which edit `claude-new/settings.template.json`, a copy).
- `claude/execute-prd/`, `claude/execute-plan/`, and `claude/_internal/` are read-only source material for this plan. Never modify them.
- Workflow scripts must not call `Date.now()`, `new Date()`, or `Math.random()` (runtime throws — breaks resume). Timestamps arrive via `args`.
- Workflow scripts have no filesystem access. Every read/parse/write happens inside an `agent()` call; the script only orchestrates.
- Skill frontmatter `name:` must match its directory name (repo rule, `claude/CLAUDE.md`).
- Skill descriptions state triggering conditions only — no workflow summaries (superpowers:writing-skills SDO rule).
- New skills reference existing contracts by path: `_internal/repo-delivery`, `_internal/disposition`, `_internal/decision-record`, `_internal/diff-manifest`, `_internal/aers-readiness`. Do not fork them into `claude-new/`.
- Branch for this work: `feat/claude-new-execute-rebuild` off `main`. Commit after every task.
- Verification commands available in this repo: `node --check` (Node 22), `jq`, `rg`. There is no test framework; each task's test cycle is its stated verification commands.

---

### Task 1: Scaffold `claude-new/` and the plan-format contract

The plan format is the shared interface between the compiler (execute-prd) and the runtime (execute-plan workflow). It must exist first because Tasks 2–9 all consume it.

**Files:**
- Create: `claude-new/README.md`
- Create: `claude-new/_internal/plan-format/SKILL.md`
- Create: `claude-new/execute-plan/tests/fixtures/toy-plan.md`

**Interfaces:**
- Produces: the plan document format (frontmatter fields, `## Task N:` sections with `depends_on:` / `milestone_end:` metadata, `**Acceptance:**` blocks) consumed by Task 2's PLAN_SCHEMA parser prompt and Task 9's authoring rules.

- [ ] **Step 1: Create the branch**

```bash
cd ~/repos/savviety-skills
git switch -c feat/claude-new-execute-rebuild main
```

- [ ] **Step 2: Write `claude-new/README.md`**

```markdown
# claude-new — rebuilt execute pipeline (staging tree)

Parallel rebuild of `claude/execute-prd` + `claude/execute-plan` per
`docs/superpowers/plans/2026-07-07-claude-new-execute-rebuild.md`.

Design: orchestration mechanics live in Workflow scripts
(`execute-plan/workflows/run-plan.mjs`), prohibitions live in
settings deny rules, commodity reviews use built-ins
(`/code-review`, `/verify`, `/security-review`), and SKILL.md files
carry only judgment (gates, taxonomies, dispositions, verdicts).

Not yet wired into `manifest.json`. Promote to `claude/` (replacing
the old pair) only after harness validation (Task 10).

| Path | Role |
|---|---|
| `_internal/plan-format/` | Plan document contract (compiler ↔ runtime interface) |
| `execute-prd/` | PRD → plan compiler skill + design-it-twice judge workflow |
| `execute-plan/` | Judgment skill + runtime workflow + toy-plan fixture |
| `settings.template.json` | Consumer settings with destructive-git deny rules |
```

- [ ] **Step 3: Write `claude-new/_internal/plan-format/SKILL.md`**

```markdown
---
name: plan-format
description: "Canonical plan document format produced by /execute-prd and consumed by /execute-plan's runtime workflow. Defines frontmatter, task metadata (depends_on, milestone_end), and mechanical acceptance blocks. Not user-invokable."
user-invocable: false
---

# Plan Format (compiler ↔ runtime contract)

A plan is a markdown file. The runtime workflow parses it via an
agent with a JSON schema; this document is the source of truth both
for the author (execute-prd step 5) and the parser prompt
(run-plan.mjs `PLAN_SCHEMA` agent).

## Frontmatter (YAML, required)

    ---
    slug: <kebab-case plan id>
    source_prd: <path or ADO/Linear ref>
    intent: <one-sentence goal, verbatim usable as pr_description>
    type: bug | feature | refactor | infra
    ---

## Body structure

- H1 title.
- `**Source:**` line referencing the original artefact.
- Optional `## Closed Decisions` — bullets; each is tablestakes for
  the runtime (workers may not re-litigate them).
- One or more `## Task N: <title>` sections, N unique and ascending.

## Task section metadata (replaces the old ## Waves / lane tables)

Each task section starts with a fenced metadata block:

    ```yaml
    depends_on: []          # task numbers that must complete first
    write_scope:            # globs this task may modify
      - src/api/**
    milestone_end: false    # true → runtime runs a review gate after it
    ```

Dependency structure IS the parallelism declaration: tasks whose
`depends_on` are all satisfied and whose `write_scope` globs are
mutually disjoint run as one parallel group in isolated worktrees.
No separate `## Waves` section, no lane registry, no max-team rule —
the runtime computes groups and caps concurrency itself.

Single-owner surfaces (root manifests, lockfiles, shared types,
migrations, generated files) must appear in exactly one task's
`write_scope`. Overlap between two dependency-independent tasks is a
validation error (execute-prd step 7 checks it; the runtime re-checks
and serialises the pair if found).

## Acceptance blocks

Each task ends with `**Acceptance:**` bullets. Every bullet must be
mechanical: a command that exits 0, or an observable with its exact
expected value. Prose like "works correctly" is a validation error.

## Milestones

`milestone_end: true` on a task triggers the runtime's review gate
after that task's group completes. If no task sets it, the runtime
treats the final task as the only milestone.
```

- [ ] **Step 4: Write the toy-plan fixture `claude-new/execute-plan/tests/fixtures/toy-plan.md`**

This fixture exercises every format feature: dependencies, a parallel-eligible pair, a milestone, closed decisions. It is used by Task 2's parser verification and Task 10's harness smoke test.

````markdown
---
slug: toy-greeter
source_prd: tests/fixtures/toy-prd.md
intent: Add a greet(name) helper and a CLI wrapper that prints it
type: feature
---

# Toy Greeter Plan

**Source:** tests/fixtures/toy-prd.md

## Closed Decisions

- Language: plain Node ESM, no dependencies.
- Output format: `Hello, <name>!` exactly.

## Task 1: greet helper

```yaml
depends_on: []
write_scope:
  - src/greet.mjs
  - test/greet.test.mjs
milestone_end: false
```

Create `src/greet.mjs` exporting `greet(name)` returning
`` `Hello, ${name}!` ``. Add `test/greet.test.mjs` using `node:test`.

**Acceptance:**
- `node --test test/greet.test.mjs` exits 0
- `node -e "import('./src/greet.mjs').then(m=>process.exit(m.greet('x')==='Hello, x!'?0:1))"` exits 0

## Task 2: CLI wrapper

```yaml
depends_on: [1]
write_scope:
  - bin/greet.mjs
milestone_end: false
```

Create `bin/greet.mjs` that prints `greet(process.argv[2])`.

**Acceptance:**
- `node bin/greet.mjs World` prints `Hello, World!`

## Task 3: README

```yaml
depends_on: [1]
write_scope:
  - README.md
milestone_end: true
```

Document usage in `README.md`.

**Acceptance:**
- `rg -q "greet" README.md` exits 0
````

- [ ] **Step 5: Verify structure and commit**

```bash
rg -c "depends_on" claude-new/_internal/plan-format/SKILL.md claude-new/execute-plan/tests/fixtures/toy-plan.md
# Expected: both files report ≥1 match
git add claude-new/
git commit -m "feat(claude-new): scaffold tree and plan-format contract"
```

---

### Task 2: Runtime workflow — parser, dependency grouping, sequential task loop

**Files:**
- Create: `claude-new/execute-plan/workflows/run-plan.mjs`

**Interfaces:**
- Consumes: plan format from Task 1; `args` object `{ planPath, planSha, baseSha, branch, commands: { install, lint, build, test, defaultBranch }, flags: { maxRetries, maxFixCycles, acceptRisk: [], adversarial }, timestamp }`.
- Produces: `parsePlan()` result shape `{ slug, intent, closedDecisions: [], tasks: [{ id, title, dependsOn: [], writeScope: [], milestoneEnd, body, acceptance: [] }] }`; `computeGroups(tasks)` returning ordered arrays of parallel-safe task groups; `runTask(task)` returning `TASK_RESULT`; module-level `state` object `{ retries, taskResults, findings, deviations }` extended by Tasks 3–5.

- [ ] **Step 1: Write the script skeleton with meta, schemas, parser, and grouping**

```javascript
export const meta = {
  name: 'execute-plan-runtime',
  description: 'Deterministic runtime for /execute-plan: task loop, review gates, parallel lanes, report',
  phases: [
    { title: 'Parse', detail: 'plan → task graph' },
    { title: 'Tasks', detail: 'implement, build, test, commit per task' },
    { title: 'Review Gates', detail: 'milestone + PR-boundary reviews with fix cycles' },
    { title: 'Report', detail: 'assemble structured result' },
  ],
}

// ---------- schemas ----------
const PLAN_SCHEMA = {
  type: 'object',
  required: ['slug', 'intent', 'tasks'],
  properties: {
    slug: { type: 'string' },
    intent: { type: 'string' },
    closedDecisions: { type: 'array', items: { type: 'string' } },
    tasks: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'title', 'dependsOn', 'writeScope', 'milestoneEnd', 'body', 'acceptance'],
        properties: {
          id: { type: 'integer' },
          title: { type: 'string' },
          dependsOn: { type: 'array', items: { type: 'integer' } },
          writeScope: { type: 'array', items: { type: 'string' } },
          milestoneEnd: { type: 'boolean' },
          body: { type: 'string' },
          acceptance: { type: 'array', items: { type: 'string' } },
        },
      },
    },
  },
}

const TASK_RESULT = {
  type: 'object',
  required: ['id', 'status'],
  properties: {
    id: { type: 'integer' },
    status: { type: 'string', enum: ['done', 'blocked'] },
    commit: { type: 'string' },
    files: { type: 'array', items: { type: 'string' } },
    failure: { type: 'string' },
    clarificationNeeded: { type: 'string' },
  },
}

// ---------- shared run state ----------
const MAX_RETRIES = args.flags?.maxRetries ?? 20
const state = { retries: 0, taskResults: [], findings: [], deviations: [] }

function spendRetry(where) {
  state.retries++
  if (state.retries > MAX_RETRIES) {
    throw new Error(`Retry budget exhausted (${MAX_RETRIES}) at ${where}. ` +
      `Resume with Workflow resumeFromRunId after diagnosing the impasse ` +
      `(superpowers:systematic-debugging).`)
  }
}

// ---------- Phase: Parse ----------
phase('Parse')
const plan = await agent(
  `Read the plan file at ${args.planPath}. It follows the plan-format contract ` +
  `(frontmatter slug/intent/type; "## Task N:" sections each opening with a ` +
  `fenced yaml block carrying depends_on, write_scope, milestone_end; ` +
  `"**Acceptance:**" bullet lists). Extract every task. Return ONLY the ` +
  `structured object. body = the task section's full markdown after the ` +
  `metadata block. acceptance = the raw bullet strings.`,
  { schema: PLAN_SCHEMA, effort: 'low', label: 'parse-plan' },
)
if (!plan) throw new Error(`Plan parse failed for ${args.planPath}`)
log(`Parsed ${plan.tasks.length} tasks from ${args.planPath}`)

// Topological grouping: a group = all unscheduled tasks whose deps are done
// AND whose write scopes are pairwise disjoint (string-compared globs; the
// compiler guarantees disjointness, this is the runtime re-check).
function scopesOverlap(a, b) {
  return a.some(x => b.some(y => x === y || x.startsWith(y.replace(/\*+.*$/, '')) || y.startsWith(x.replace(/\*+.*$/, ''))))
}
function computeGroups(tasks) {
  const done = new Set(); const groups = []
  const pending = [...tasks].sort((a, b) => a.id - b.id)
  while (done.size < tasks.length) {
    const ready = pending.filter(t => !done.has(t.id) && t.dependsOn.every(d => done.has(d)))
    if (!ready.length) throw new Error('Dependency cycle in plan task graph')
    const group = []
    for (const t of ready) {
      if (group.every(g => !scopesOverlap(g.writeScope, t.writeScope))) group.push(t)
    }
    group.forEach(t => done.add(t.id))
    groups.push(group)
  }
  return groups
}
const groups = computeGroups(plan.tasks)
log(`Task graph → ${groups.length} sequential group(s); sizes: ${groups.map(g => g.length).join(', ')}`)
```

- [ ] **Step 2: Append the per-task implementer and sequential loop**

```javascript
// ---------- Phase: Tasks ----------
const CO_TENANCY = 'You are not alone in the codebase. Own only your assigned ' +
  'write scope. If the task requires editing a file outside it, stop and set ' +
  'clarificationNeeded instead of editing.'

function implPrompt(task, attempt, priorFailure) {
  return [
    `Implement Task ${task.id} ("${task.title}") from ${args.planPath}.`,
    `Repo branch: ${args.branch}. Follow the plan exactly — no unplanned improvements.`,
    plan.closedDecisions?.length
      ? `Closed decisions (tablestakes — execute as stated, never re-litigate):\n- ${plan.closedDecisions.join('\n- ')}`
      : '',
    `Task spec:\n${task.body}`,
    `Write scope (only these globs): ${task.writeScope.join(', ')}. ${CO_TENANCY}`,
    `TDD: if an acceptance bullet names a test that doesn't exist, write it ` +
    `first and see it fail before implementing.`,
    `Acceptance (ALL must pass):\n- ${task.acceptance.join('\n- ')}`,
    `Then run build ("${args.commands.build}") and tests ("${args.commands.test}").`,
    `Commit with subject "<type>(<scope>): <desc>" and trailer lines:\n` +
    `Task ${task.id} from ${args.planPath}\nPlan-SHA: ${args.planSha}\nBase-SHA: ${args.baseSha}`,
    attempt > 1 ? `Attempt ${attempt}. Prior failure:\n${priorFailure}` : '',
    `Return status done only if acceptance, build, and tests all pass.`,
  ].filter(Boolean).join('\n\n')
}

async function runTask(task, opts = {}) {
  let failure = ''
  for (let attempt = 1; attempt <= 3; attempt++) {
    if (attempt > 1) spendRetry(`task ${task.id} attempt ${attempt}`)
    const r = await agent(implPrompt(task, attempt, failure),
      { schema: TASK_RESULT, phase: 'Tasks', label: `task:${task.id}`, ...opts })
    if (r?.clarificationNeeded) {
      return { id: task.id, status: 'blocked', failure: `AMBIGUITY: ${r.clarificationNeeded}` }
    }
    if (r?.status === 'done') return r
    failure = r?.failure ?? 'agent returned no result'
  }
  return { id: task.id, status: 'blocked', failure }
}

phase('Tasks')
for (const group of groups) {
  if (group.length === 1) {
    const r = await runTask(group[0])
    state.taskResults.push(r)
    if (r.status === 'blocked') throw new Error(`Task ${r.id} BLOCKED: ${r.failure}`)
  } else {
    await runParallelGroup(group)   // Task 4 of the plan defines this
  }
  const gateTask = group.find(t => t.milestoneEnd)
  if (gateTask) await reviewGate('breakpoint', `milestone after task ${gateTask.id}`)  // Task 3 defines reviewGate
}
```

- [ ] **Step 3: Add temporary stubs so the file parses until Tasks 3–4 replace them**

```javascript
// ---- stubs (replaced by later plan tasks) ----
async function runParallelGroup(group) {
  for (const t of group) {                       // sequential fallback until Task 4
    const r = await runTask(t)
    state.taskResults.push(r)
    if (r.status === 'blocked') throw new Error(`Task ${r.id} BLOCKED: ${r.failure}`)
  }
}
async function reviewGate(profile, where) { log(`reviewGate(${profile}) at ${where} — stub`) }

return { schema_version: 1, ...state }
```

- [ ] **Step 4: Syntax-verify and commit**

`node --check` cannot see the workflow globals (`agent`, `phase`, `log`, `args`, `parallel`, `budget`), so prepend declarations only for the check:

```bash
cd ~/repos/savviety-skills
{ echo 'const agent=0,phase=0,log=0,args=0,parallel=0,pipeline=0,budget=0,workflow=0;'; cat claude-new/execute-plan/workflows/run-plan.mjs; } > /tmp/wfcheck.mjs
node --check /tmp/wfcheck.mjs && echo SYNTAX-OK
# Expected: SYNTAX-OK  (top-level await/return are legal in the workflow runtime;
# if node flags the bare `return`, wrap the file's body check only — the runtime
# executes scripts in an async function context. Acceptable fallback:
# node -e "import('node:fs').then(f=>{new (async function(){}).constructor(f.readFileSync('/tmp/wfcheck.mjs','utf8').replace('export const meta','const meta'))})" && echo SYNTAX-OK
git add claude-new/execute-plan/workflows/run-plan.mjs
git commit -m "feat(claude-new): runtime workflow — parser, grouping, sequential task loop"
```

---

### Task 3: Runtime workflow — review gates with coded fix cycles

Replaces the `reviewGate` stub. This is where the old Phase 2.5/3b "max 3 auto-fix cycles per finding" prose becomes an actual `for` loop.

**Files:**
- Modify: `claude-new/execute-plan/workflows/run-plan.mjs` (replace the `reviewGate` stub)

**Interfaces:**
- Consumes: `state`, `spendRetry`, `args.flags.acceptRisk`, `args.flags.maxFixCycles` (default 3).
- Produces: `reviewGate(profile, where)` pushing finding objects `{ id, severity, file, line, summary, status, where }` into `state.findings`; statuses use the `_internal/disposition` vocabulary (`fixed | open | accepted-risk`).

- [ ] **Step 1: Replace the stub with the real gate**

```javascript
const FINDINGS_SCHEMA = {
  type: 'object', required: ['findings'],
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object', required: ['id', 'severity', 'file', 'summary'],
        properties: {
          id: { type: 'string' },
          severity: { type: 'string', enum: ['critical', 'major', 'minor', 'nit', 'plan-deviation'] },
          file: { type: 'string' }, line: { type: 'integer' },
          summary: { type: 'string' }, fix: { type: 'string' },
        },
      },
    },
  },
}
const FIX_RESULT = {
  type: 'object', required: ['status'],
  properties: { status: { type: 'string', enum: ['fixed', 'failed'] }, commit: { type: 'string' }, note: { type: 'string' } },
}

async function reviewGate(profile, where) {
  const range = `${args.baseSha}..HEAD`
  const reviewPrompt = profile === 'breakpoint'
    ? `Run the built-in /code-review skill at medium effort on the diff ${range} ` +
      `(exclude ${args.planPath} and docs/decisions/**). Intent: ${plan.intent}. ` +
      `Return every finding as structured output.`
    : `Invoke the domain-review skill (Skill tool) with profile: full on the diff ` +
      `${range} (exclude ${args.planPath} and docs/decisions/**), ` +
      `pr_description: "${plan.intent}". Return its merged findings as structured output.`
  const review = await agent(reviewPrompt,
    { schema: FINDINGS_SCHEMA, phase: 'Review Gates', label: `review:${where}` })
  const findings = (review?.findings ?? []).map(f => ({ ...f, where, status: 'open' }))

  for (const f of findings) {
    const blocking = f.severity === 'critical' || f.severity === 'major'
    if (!blocking) { state.findings.push(f); continue }
    if (args.flags?.acceptRisk?.includes(f.id)) { f.status = 'accepted-risk'; state.findings.push(f); continue }
    const maxCycles = args.flags?.maxFixCycles ?? 3
    for (let cycle = 1; cycle <= maxCycles && f.status !== 'fixed'; cycle++) {
      spendRetry(`fix ${f.id} cycle ${cycle}`)
      const fix = await agent(
        `Fix review finding ${f.id} (${f.severity}) at ${f.file}${f.line ? ':' + f.line : ''}: ` +
        `${f.summary}\nSuggested fix: ${f.fix ?? 'none given'}\n` +
        `Make the minimal correct change, run build ("${args.commands.build}") and ` +
        `tests ("${args.commands.test}"), then commit with subject ` +
        `"review(${profile}): fix ${f.id} — <summary>" and trailer "Plan-SHA: ${args.planSha}". ` +
        `NEVER include a "Task N from" footer on a review-fix commit.`,
        { schema: FIX_RESULT, phase: 'Review Gates', label: `fix:${f.id}` })
      if (fix?.status === 'fixed') f.status = 'fixed'
    }
    state.findings.push(f)
    if (f.status === 'open') {
      throw new Error(`Finding ${f.id} (${f.severity}) still open after fix cycles at ${where}. ` +
        `Re-run with acceptRisk including "${f.id}" to accept, or fix manually and resume.`)
    }
  }
  log(`${where}: ${findings.length} finding(s) — ` +
      `${findings.filter(f => f.status === 'fixed').length} fixed, ` +
      `${findings.filter(f => f.status === 'accepted-risk').length} accepted-risk, ` +
      `${findings.filter(f => f.status === 'open').length} open (non-blocking)`)
}
```

- [ ] **Step 2: Re-run the Task 2 Step 4 syntax check; commit**

```bash
git add claude-new/execute-plan/workflows/run-plan.mjs
git commit -m "feat(claude-new): runtime workflow — review gates with coded fix cycles"
```

---

### Task 4: Runtime workflow — parallel groups in worktrees + sequential merge

Replaces the `runParallelGroup` stub. Worktree creation/install/cleanup is delegated to `isolation: 'worktree'`; merge ordering stays deterministic in code.

**Files:**
- Modify: `claude-new/execute-plan/workflows/run-plan.mjs` (replace the `runParallelGroup` stub)

**Interfaces:**
- Consumes: `runTask`, `state`, `args.commands`.
- Produces: `runParallelGroup(group)` — dispatches all lanes concurrently, then merges lane branches smallest-diff-first (dependency order inside a group is impossible by construction: group members are dependency-independent).

- [ ] **Step 1: Replace the stub**

```javascript
async function runParallelGroup(group) {
  log(`Parallel group: tasks ${group.map(t => t.id).join(', ')} in isolated worktrees`)
  const lanes = await parallel(group.map(t => () =>
    runTask(t, { isolation: 'worktree' }).then(r => ({ task: t, result: r }))
  ))
  const usable = lanes.filter(Boolean)
  for (const { result } of usable) state.taskResults.push(result)
  const blocked = usable.filter(l => l.result.status === 'blocked')
  if (blocked.length || usable.length < group.length) {
    throw new Error(`Parallel group failed: ` +
      blocked.map(l => `Task ${l.result.id}: ${l.result.failure}`).join('; ') +
      (usable.length < group.length ? '; plus lane(s) lost to agent error' : ''))
  }
  // Sequential merge, smallest diff first (fewest rebase surfaces for the rest).
  const ordered = [...usable].sort((a, b) => (a.result.files?.length ?? 0) - (b.result.files?.length ?? 0))
  for (const { task, result } of ordered) {
    const merge = await agent(
      `Lane for Task ${task.id} committed ${result.commit} on its worktree branch. ` +
      `Locate that branch (git branch --contains ${result.commit}), merge it into the ` +
      `run branch "${args.branch}" (merge commit; NEVER reset --hard, NEVER force-push), ` +
      `resolve conflicts favouring already-merged lanes, then run ` +
      `"${args.commands.build}" and "${args.commands.test}" on ${args.branch}. ` +
      `Return status done only if both pass after the merge.`,
      { schema: TASK_RESULT, phase: 'Tasks', label: `merge:task-${task.id}` })
    if (merge?.status !== 'done') {
      throw new Error(`Merge of task ${task.id} lane failed: ${merge?.failure ?? 'no result'}. ` +
        `All lane branches are preserved; resolve manually and resume.`)
    }
  }
  log(`Group merged: build+test green on ${args.branch} after each lane`)
}
```

- [ ] **Step 2: Syntax check (Task 2 Step 4 command); commit**

```bash
git add claude-new/execute-plan/workflows/run-plan.mjs
git commit -m "feat(claude-new): runtime workflow — worktree lanes and sequential merge"
```

---

### Task 5: Runtime workflow — PR-boundary stack, plan alignment, report return

**Files:**
- Modify: `claude-new/execute-plan/workflows/run-plan.mjs` (replace the final stub `return` with the real Phase: Report)

**Interfaces:**
- Consumes: everything above.
- Produces: the workflow return value — the execution-report object the SKILL.md (Task 6) renders. Shape: `{ schema_version, verdict, plan_file, plan_sha, base_sha, branch, tasks, findings, deviations, retry_stats, adversarial }`.

- [ ] **Step 1: Replace the trailing stub return with the PR-boundary sequence**

```javascript
// ---------- Phase: Review Gates (PR boundary) ----------
phase('Review Gates')
const checkpoint = await agent(
  `Final quality gate on branch ${args.branch}: run lint ("${args.commands.lint}"), ` +
  `build ("${args.commands.build}"), tests ("${args.commands.test}"). If the diff ` +
  `${args.baseSha}..HEAD touches product source (not just tests/docs/config), also ` +
  `invoke the built-in /verify skill to exercise the changed flow end-to-end. ` +
  `Return status done only if all pass.`,
  { schema: TASK_RESULT, label: 'checkpoint' })
if (checkpoint?.status !== 'done') throw new Error(`Checkpoint failed: ${checkpoint?.failure}`)

await reviewGate('full', 'pr-boundary')

const DEVIATIONS_SCHEMA = {
  type: 'object', required: ['allTasksImplemented', 'deviations'],
  properties: {
    allTasksImplemented: { type: 'boolean' },
    deviations: {
      type: 'array',
      items: {
        type: 'object', required: ['id', 'summary', 'category'],
        properties: {
          id: { type: 'string' }, file: { type: 'string' }, summary: { type: 'string' },
          category: { type: 'string', enum: ['lockfile', 'dep-patch-bump', 'formatter', 'auto-generated-files', 'unmatched'] },
        },
      },
    },
  },
}
const alignment = await agent(
  `Plan-alignment check: re-read ${args.planPath}, compare against the diff ` +
  `${args.baseSha}..HEAD. Verify every task is implemented as specified. List every ` +
  `unplanned change as a deviation, classifying per these canonical categories: ` +
  `lockfile (only lock files changed), dep-patch-bump (semver patch-only version ` +
  `bump), formatter (whitespace/quotes only, no AST change — if unsure it does NOT ` +
  `qualify), auto-generated-files, else unmatched.`,
  { schema: DEVIATIONS_SCHEMA, label: 'plan-alignment' })
const AUTO_ACCEPT = ['lockfile', 'dep-patch-bump', 'formatter', 'auto-generated-files']
for (const d of alignment?.deviations ?? []) {
  d.status = AUTO_ACCEPT.includes(d.category) ? 'disagree-with-evidence'
    : args.flags?.acceptRisk?.includes(d.id) ? 'accepted-risk' : 'open'
  state.deviations.push(d)
}
const openDeviations = state.deviations.filter(d => d.status === 'open')
if (openDeviations.length) {
  throw new Error(`Unmatched plan deviations require disposition: ` +
    openDeviations.map(d => `${d.id}: ${d.summary}`).join('; ') +
    `. Re-run with acceptRisk for accepted ones, or amend the plan.`)
}

// Adversarial review: flag-driven, cross-model when available.
let adversarial = { status: 'skipped', reason: 'flag=never or below threshold' }
const bigDiff = state.taskResults.flatMap(t => t.files ?? []).length >= 10
if (args.flags?.adversarial === 'always' || (args.flags?.adversarial === 'auto' && bigDiff)) {
  const adv = await agent(
    `Invoke the review-adversarial skill on diff ${args.baseSha}..HEAD with intent ` +
    `"${plan.intent}". If its cross-model CLIs are unavailable, run the built-in ` +
    `/code-review at high effort instead and say which path you took. Return findings.`,
    { schema: FINDINGS_SCHEMA, label: 'adversarial' })
  adversarial = { status: 'ran', findings: adv?.findings ?? [] }
}

// ---------- Phase: Report ----------
phase('Report')
const blockingOpen = state.findings.filter(f => f.status === 'open' && ['critical', 'major'].includes(f.severity))
const verdict = blockingOpen.length ? 'FAIL'
  : (state.findings.some(f => f.status !== 'fixed') || state.deviations.length) ? 'WARN' : 'PASS'
return {
  schema_version: 1,
  verdict,
  plan_file: args.planPath, plan_sha: args.planSha,
  base_sha: args.baseSha, branch: args.branch,
  tasks: state.taskResults,
  findings: state.findings,
  deviations: state.deviations,
  retry_stats: { total_retries: state.retries, budget: MAX_RETRIES },
  adversarial,
  run_started: args.timestamp,
}
```

- [ ] **Step 2: Syntax check; then structural check that no stubs remain; commit**

```bash
rg -n "stub" claude-new/execute-plan/workflows/run-plan.mjs
# Expected: no matches
git add claude-new/execute-plan/workflows/run-plan.mjs
git commit -m "feat(claude-new): runtime workflow — PR boundary, alignment, report"
```

---

### Task 6: The slim `execute-plan` judgment skill

**Files:**
- Create: `claude-new/execute-plan/SKILL.md`

**Interfaces:**
- Consumes: `run-plan.mjs` (invoked via the Workflow tool with `scriptPath`), `/validate-plan`, `_internal/repo-delivery`, `_internal/disposition`, `_internal/decision-record`.
- Produces: the user-facing `/execute-plan` behaviour.

- [ ] **Step 1: Write the SKILL.md**

Frontmatter and structure below are complete; the three sections marked *(copy verbatim)* are lifted from the old skill unchanged — they are the judgment content this rebuild preserves. Source: `claude/execute-plan/SKILL.md` at commit `036dc9d`.

```markdown
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
4. **Pre-execution clarification (codebase-aware).** *(copy verbatim:
   old skill "Phase 1.5" body, lines 516–586 — the
   ambiguity-vs-uncertainty heuristic, the three ambiguity categories,
   what is NOT ambiguity.)* Interactive session → surface each
   ambiguity with AskUserQuestion and record the answer as a closed
   decision appended to the plan (this changes planSha — recompute).
   Autonomous session → halt listing the ambiguities as open questions.

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

While it runs, do not implement tasks yourself — the workflow owns
execution. On a thrown error the run is preserved (worktree branches
and commits stay); diagnose, then resume with the same scriptPath and
`resumeFromRunId` from the failed run — completed agent calls replay
from cache.

## Interpreting the result

The workflow returns the report object. Write
`execution-report.json` verbatim and render `execution-report.md`
from it (tables: per-task, findings with disposition statuses,
deviations, retry stats). Verdict rules *(copy verbatim: old skill
"Verdict rules", lines 1469–1492)*.

Disposition vocabulary and end-state rules are canonical in
`_internal/disposition/SKILL.md`; the workflow emits statuses from
that vocabulary and this skill never invents new ones.

## Decision records

Write records per `_internal/decision-record/SKILL.md` for choices a
future run could plausibly reverse — ambiguity resolutions from
preflight gate 4 and accepted-risk deviations always qualify.

## Postmortem

Fire when verdict is WARN/FAIL, the retry budget was exhausted, or
any deviation ended accepted-risk. *(copy verbatim: old skill Phase 5
"Markdown structure", "Recommendation taxonomy", "Hard rules" and
"Cross-run aggregation" — lines 1547–1729.)* Output lands next to the
execution report; append to `docs/postmortems/index.json`.

## Enforcement notes (not prose rules — actual config)

Destructive git commands are denied by `settings.template.json`
permissions (`git reset --hard`, `git push --force*`, `git clean -f`,
`git branch -D`). This skill assumes those rules are installed; it
does not restate them as instructions.

## When NOT to Use

- No plan exists — use `/execute-prd` (PRD input) or
  superpowers:writing-plans (ad-hoc).
- Plan doesn't follow the plan-format contract —
  superpowers:executing-plans is the lighter general executor.
- Trivial single-file change — edit directly.
```

- [ ] **Step 2: Verify the verbatim-copy sections were actually copied (no dangling markers) and frontmatter name matches**

```bash
rg -n "copy verbatim" claude-new/execute-plan/SKILL.md
# Expected: no matches — every marker replaced with real copied text
awk '/^name:/{print $2; exit}' claude-new/execute-plan/SKILL.md
# Expected: execute-plan
git add claude-new/execute-plan/SKILL.md
git commit -m "feat(claude-new): slim execute-plan judgment skill"
```

---

### Task 7: Enforcement — deny rules and default-branch commit guard

**Files:**
- Create: `claude-new/settings.template.json` (start from a copy of `claude/settings.template.json`)
- Create: `claude-new/infra/hooks/default-branch-guard.sh`

**Interfaces:**
- Produces: consumer-repo settings installed by the manifest (when claude-new is promoted); referenced by Task 6's "Enforcement notes".

- [ ] **Step 1: Copy and extend the settings template**

```bash
cp claude/settings.template.json claude-new/settings.template.json
```

Then merge into its `permissions` object (preserve existing keys):

```json
{
  "permissions": {
    "deny": [
      "Bash(git reset --hard*)",
      "Bash(git push --force *)",
      "Bash(git push --force)",
      "Bash(git push -f*)",
      "Bash(git clean -f*)",
      "Bash(git branch -D*)",
      "Bash(rtk git reset --hard*)",
      "Bash(rtk git push --force*)",
      "Bash(rtk git push -f*)",
      "Bash(rtk git clean -f*)",
      "Bash(rtk git branch -D*)"
    ]
  }
}
```

Note: `git push --force-with-lease` must remain allowed (lane rebases use it); the pattern `git push --force *` plus bare `git push --force` deny the plain force-push without catching `--force-with-lease`. Verify ordering does not shadow: deny rules are exact/prefix — `--force-with-lease` does not match `--force ` (trailing space) or bare `--force`.

- [ ] **Step 2: Write the default-branch commit guard hook**

`claude-new/infra/hooks/default-branch-guard.sh`:

```bash
#!/bin/sh
# PreToolUse hook (matcher: Bash, if: "Bash(git commit*)").
# Blocks commits on the repo's default branch during execute-plan runs.
input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty')
case "$cmd" in
  *"git commit"*) ;;
  *) exit 0 ;;
esac
branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null) || exit 0
default=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|.*/||')
[ -z "$default" ] && default=main
if [ "$branch" = "$default" ]; then
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Commit on default branch %s blocked — create a feature branch (execute-plan policy)."}}\n' "$default"
fi
exit 0
```

Register it in `claude-new/settings.template.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "if": "Bash(git commit*)", "command": ".claude/hooks/default-branch-guard.sh", "timeout": 10 }
        ]
      }
    ]
  }
}
```

- [ ] **Step 3: Pipe-test the hook and validate the JSON**

```bash
chmod +x claude-new/infra/hooks/default-branch-guard.sh
echo '{"tool_name":"Bash","tool_input":{"command":"git commit -m x"}}' | claude-new/infra/hooks/default-branch-guard.sh
# Expected on this repo when on main: a JSON deny decision. On a feature branch: empty output, exit 0.
echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' | claude-new/infra/hooks/default-branch-guard.sh; echo "exit=$?"
# Expected: empty output, exit=0
jq -e '.permissions.deny | length >= 10' claude-new/settings.template.json
jq -e '.hooks.PreToolUse[0].hooks[0].command' claude-new/settings.template.json
git add claude-new/settings.template.json claude-new/infra/
git commit -m "feat(claude-new): destructive-git deny rules and default-branch guard hook"
```

---

### Task 8: execute-prd — design-it-twice judge-panel workflow

**Files:**
- Create: `claude-new/execute-prd/workflows/design-it-twice.mjs`

**Interfaces:**
- Consumes: `args = { decision, contextSummary, repoAuditPath }`.
- Produces: return object `{ options: [{ constraint, interface, usageExample, hides, tradeoffs }], recommendation, rationale }` consumed by execute-prd step 4.5 (Task 9).

- [ ] **Step 1: Write the script**

```javascript
export const meta = {
  name: 'design-it-twice',
  description: 'Three parallel design explorations under different constraints, judged and synthesized',
  phases: [{ title: 'Explore' }, { title: 'Judge' }],
}

const DESIGN_SCHEMA = {
  type: 'object', required: ['constraint', 'interface', 'usageExample', 'hides', 'tradeoffs'],
  properties: {
    constraint: { type: 'string' }, interface: { type: 'string' },
    usageExample: { type: 'string' }, hides: { type: 'string' }, tradeoffs: { type: 'string' },
  },
}
const JUDGE_SCHEMA = {
  type: 'object', required: ['recommendation', 'rationale'],
  properties: { recommendation: { type: 'string' }, rationale: { type: 'string' } },
}

const CONSTRAINTS = [
  ['minimal-surface', 'Minimize surface area: 1–3 methods/endpoints max, hide everything else.'],
  ['max-flexibility', 'Maximize flexibility: support the most use cases, extensible.'],
  ['common-case', 'Optimize the common case: make the 80% path trivial; accept edge-case trade-offs.'],
]

phase('Explore')
const options = (await parallel(CONSTRAINTS.map(([key, constraint]) => () =>
  agent(
    `Design decision: ${args.decision}\nContext: ${args.contextSummary}\n` +
    `Repo audit: read ${args.repoAuditPath} for existing patterns.\n` +
    `Design under this constraint ONLY: ${constraint}\n` +
    `Return the interface signature, a usage example, what it hides, and trade-offs.`,
    { schema: DESIGN_SCHEMA, label: `design:${key}`, phase: 'Explore' })
))).filter(Boolean)
if (options.length < 2) throw new Error('Design exploration produced fewer than 2 options')

phase('Judge')
const judge = await agent(
  `Judge these ${options.length} designs for: ${args.decision}\n` +
  options.map((o, i) => `--- Option ${i + 1} (${o.constraint})\n${o.interface}\n${o.usageExample}\nHides: ${o.hides}\nTrade-offs: ${o.tradeoffs}`).join('\n') +
  `\nCriteria: interface simplicity; depth (small surface hiding complex internals); ` +
  `implementation efficiency; ease of correct use vs ease of misuse. ` +
  `Recommend one shape (synthesis allowed) with rationale.`,
  { schema: JUDGE_SCHEMA, label: 'judge', effort: 'high' })

return { options, recommendation: judge.recommendation, rationale: judge.rationale }
```

- [ ] **Step 2: Syntax check (same technique as Task 2 Step 4); commit**

```bash
git add claude-new/execute-prd/workflows/design-it-twice.mjs
git commit -m "feat(claude-new): design-it-twice judge-panel workflow"
```

---

### Task 9: The trimmed `execute-prd` compiler skill

**Files:**
- Create: `claude-new/execute-prd/SKILL.md`

**Interfaces:**
- Consumes: `_internal/aers-readiness`, `/audit-existing`, `/validate-plan`, `workflows/design-it-twice.mjs`, plan-format contract (Task 1).
- Produces: plans in the plan-format contract; hands off to `claude-new/execute-plan`.

- [ ] **Step 1: Write the SKILL.md**

Sections marked *(copy verbatim)* come from `claude/execute-prd/SKILL.md` at commit `036dc9d`.

```markdown
---
name: execute-prd
description: "Use when a written requirements source exists (PRD, RFC, prompt.md, spec file, or ADO/Linear ticket) and the user wants it planned and built — phrases like 'build this PRD', 'execute prompt.md', 'turn this RFC into a plan and run it'. Not for vague ideas (use superpowers:brainstorming) or when a validated plan already exists (use /execute-plan)."
---

# /execute-prd — PRD to Plan Compiler

Converts a requirements source into a plan conforming to
`_internal/plan-format`, validates it, and hands off to
`/execute-plan`. After the plan is written, the plan governs
execution; the PRD is used only for traceability.

## Workflow

1. **Load repo contract** — `CLAUDE.md ## Commands` per
   `_internal/repo-delivery`; missing → halt (same message as
   /execute-plan preflight gate 1).
2. **Load requirements source** *(copy verbatim: old skill step 2
   resolution order + step 2.5 classification table, lines 55–90).*
3. **Audit current state** — invoke `/audit-existing`; never assume
   the source describes the repo accurately.
4. **Readiness gate** *(copy verbatim: old skill step 3.5,
   lines 100–130 — verdict behaviours for Ready / Partially ready /
   Not ready, interactive vs autonomous).* Use AskUserQuestion for
   interactive gap questions.
5. **Extract non-negotiables** — MUST/SHOULD requirements,
   invariants, acceptance criteria, forbidden behaviours; carry into
   task acceptance blocks and the final traceability task.
6. **Design-it-twice gate** — fire only when: type is
   feature/refactor AND the audit reveals a significant new
   architectural decision (service boundary, data model, public API,
   module interface) AND no closed decision resolves it. When it
   fires, invoke the Workflow tool with
   `scriptPath: <this-skill-dir>/workflows/design-it-twice.mjs`,
   `args: { decision, contextSummary, repoAuditPath }`. Record the
   returned recommendation as a Closed Decision in the plan,
   citing the rejected options.
7. **Draft the plan** in the `_internal/plan-format` contract:
   frontmatter (slug/source_prd/intent/type), Closed Decisions,
   `## Task N:` sections each with the yaml metadata block
   (depends_on / write_scope / milestone_end) and mechanical
   `**Acceptance:**` bullets. Shape tasks by type *(copy verbatim:
   old skill step 5 type-shape bullets, lines 187–199)*. Authoring
   rules *(copy verbatim: old skill "Plan Authoring Rules",
   lines 309–331)*. Dependency metadata replaces the old
   `## Waves` / lane tables entirely: contract-producing tasks are
   simply dependencies of their consumers, and single-owner surfaces
   appear in exactly one task's write_scope.
8. **Static plan checks** (author-side, before /validate-plan):
   every depends_on references an existing task id; no two
   dependency-independent tasks share a write_scope glob; every
   acceptance bullet is mechanical. Fix violations before validating.
9. **Validate** — run `/validate-plan`; fix-and-revalidate at most 3
   times, then surface the top blocking finding and ask the operator
   (escalate to readiness / manual override / abandon).
10. **Execute** — invoke `/execute-plan <plan-path>` with any
    pass-through flags.

## Things you must not do

*(copy verbatim: old skill "Things you must not do", lines 365–377.)*

## When NOT to Use

- A validated plan already exists — `/execute-plan` directly.
- One-or-two-file change — edit directly.
- The PRD is open-ended or the user wants to think interactively —
  `/prd-validate` or superpowers:brainstorming first.
```

- [ ] **Step 2: Verify copies resolved and name matches; commit**

```bash
rg -n "copy verbatim" claude-new/execute-prd/SKILL.md
# Expected: no matches
awk '/^name:/{print $2; exit}' claude-new/execute-prd/SKILL.md
# Expected: execute-prd
git add claude-new/execute-prd/SKILL.md
git commit -m "feat(claude-new): trimmed execute-prd compiler skill"
```

---

### Task 10: Lint, fixture smoke test, and handoff documentation

**Files:**
- Create: `claude-new/execute-plan/tests/smoke.md` (harness runbook)
- Modify: `claude-new/README.md` (add validation status)

**Interfaces:**
- Consumes: everything above.
- Produces: evidence the tree is promotable; a runbook a fresh session can follow.

- [ ] **Step 1: Structural lint across the new tree**

```bash
for f in claude-new/execute-prd/SKILL.md claude-new/execute-plan/SKILL.md claude-new/_internal/plan-format/SKILL.md; do
  d=$(basename "$(dirname "$f")"); n=$(awk '/^name:/{print $2; exit}' "$f")
  [ "$d" = "$n" ] && echo "OK $f" || echo "MISMATCH $f ($n != $d)"
done
# Expected: three OK lines
rg -n "code-review[^-]" claude-new/ | rg -v "built-in|/code-review at|/code-review skill"
# Expected: no matches (only built-in references allowed; the custom controller is domain-review)
{ echo 'const agent=0,phase=0,log=0,args=0,parallel=0,pipeline=0,budget=0,workflow=0;'; cat claude-new/execute-plan/workflows/run-plan.mjs; } > /tmp/w1.mjs && node --check /tmp/w1.mjs && echo RUNTIME-OK
{ echo 'const agent=0,phase=0,log=0,args=0,parallel=0,pipeline=0,budget=0,workflow=0;'; cat claude-new/execute-prd/workflows/design-it-twice.mjs; } > /tmp/w2.mjs && node --check /tmp/w2.mjs && echo JUDGE-OK
```

- [ ] **Step 2: Write the harness smoke runbook `claude-new/execute-plan/tests/smoke.md`**

```markdown
# claude-new smoke test (run in the skills-test harness, fresh session)

1. Sync: `cli/skill.sh --claude --update ~/repos/skills-test-harness/claude-test`
   then manually copy `claude-new/execute-plan` and `claude-new/execute-prd`
   over the installed pair in the harness `.claude/skills/` (claude-new is
   not yet in manifest.json).
2. In the harness repo, create `CLAUDE.md ## Commands` declaring
   install/lint/build/test for a toy Node project, and an empty git repo
   on a feature branch.
3. Copy `tests/fixtures/toy-plan.md` to `docs/plans/toy-plan.md`.
4. Fresh session: `/execute-plan docs/plans/toy-plan.md`.
   PASS criteria:
   - Preflight refuses on main, proceeds on a feature branch.
   - Workflow launches (visible in /workflows) with Parse → Tasks →
     Review Gates → Report phases.
   - Task 2 and Task 3 run as a parallel group in worktrees (both depend
     only on Task 1 and have disjoint write scopes).
   - A review gate fires after Task 3 (milestone_end: true).
   - execution-report.json is written with verdict PASS and 3 task rows.
5. Kill the run mid-Tasks once and resume with resumeFromRunId; verify
   completed agent calls replay from cache.
6. `/execute-prd tests/fixtures/toy-prd.md` (write a 5-line toy PRD):
   verify the emitted plan conforms to _internal/plan-format and that
   step 8's static checks reject a deliberately-overlapping write_scope.
```

- [ ] **Step 3: Record status in README and commit**

Append to `claude-new/README.md`:

```markdown
## Validation status

- [x] Structural lint (names, no stale code-review refs, workflow syntax)
- [ ] Harness smoke test (`execute-plan/tests/smoke.md`) — requires interactive session
- [ ] Promotion decision: replace `claude/execute-{prd,plan}` + manifest wiring — separate PR after smoke passes
```

```bash
git add claude-new/
git commit -m "feat(claude-new): lint evidence and harness smoke runbook"
```

---

## Deliberate deviations from the old skills (for the reviewer)

| Old mechanism | This plan | Why |
|---|---|---|
| `--max-minutes` wall-clock budget | Dropped; retry counter stays, token budget available via Workflow `budget` | Scripts cannot read the clock (no `Date`); harness-level concern |
| `## Waves` / lane tables / max-4-teams | `depends_on` + `write_scope` metadata; runtime computes groups | Parallelism is derived, not authored; runtime caps concurrency itself |
| Prose worktree mechanics + `{install_cmd}` | `isolation: 'worktree'` + implementer runs install if needed | Harness-managed |
| TTY detection for `--interactive` | AskUserQuestion when interactive; halt-with-open-questions when autonomous | Harness distinguishes the modes natively |
| implementer/reviewer/fixer template files | Inline prompts in the workflow script | Templates existed to keep prose DRY; code composes prompts directly |
| Commit-footer scanning for `--resume` | Workflow `resumeFromRunId` journal (Plan-SHA trailers kept as git-side audit) | Journal replay is exact; footers were a heuristic |
| Proof accounting table | Built-in `/verify` at checkpoint + acceptance-block TDD rule | Verify drives the flow instead of auditing test existence |
| Prose "never reset --hard / force-push" | settings deny rules + PreToolUse guard | Enforced, not remembered |

## Out of scope (explicitly)

- Modifying `manifest.json`, `claude/`, `copilot/`, `codex/`, or `kimi/` — promotion is a separate PR after the smoke test.
- Porting `validate-plan`, `domain-review`, `audit-existing`, or the `_internal` contracts — the new skills call the existing ones.
- The postmortem cross-run aggregator (`/process-tune`) — unchanged, consumes the same index format.
