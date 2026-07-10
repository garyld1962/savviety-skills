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

const cfg = typeof args === 'string' ? JSON.parse(args) : args

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

// ---------- shared run state ----------
const MAX_RETRIES = cfg.flags?.maxRetries ?? 20
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
  `Read the plan file at ${cfg.planPath}. It follows the plan-format contract ` +
  `(frontmatter slug/intent/type; "## Task N:" sections each opening with a ` +
  `fenced yaml block carrying depends_on, write_scope, milestone_end; ` +
  `"**Acceptance:**" bullet lists). Extract every task. Return ONLY the ` +
  `structured object. body = the task section's full markdown after the ` +
  `metadata block. acceptance = the raw bullet strings.`,
  { schema: PLAN_SCHEMA, effort: 'low', label: 'parse-plan' },
)
if (!plan) throw new Error(`Plan parse failed for ${cfg.planPath}`)
log(`Parsed ${plan.tasks.length} tasks from ${cfg.planPath}`)

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

// ---------- Phase: Tasks ----------
const CO_TENANCY = 'You are not alone in the codebase. Own only your assigned ' +
  'write scope. If the task requires editing a file outside it, stop and set ' +
  'clarificationNeeded instead of editing.'

function implPrompt(task, attempt, priorFailure) {
  return [
    `Implement Task ${task.id} ("${task.title}") from ${cfg.planPath}.`,
    `Repo branch: ${cfg.branch}. Follow the plan exactly — no unplanned improvements.`,
    plan.closedDecisions?.length
      ? `Closed decisions (tablestakes — execute as stated, never re-litigate):\n- ${plan.closedDecisions.join('\n- ')}`
      : '',
    `Task spec:\n${task.body}`,
    `Write scope (only these globs): ${task.writeScope.join(', ')}. ${CO_TENANCY}`,
    `TDD: if an acceptance bullet names a test that doesn't exist, write it ` +
    `first and see it fail before implementing.`,
    `Acceptance (ALL must pass):\n- ${task.acceptance.join('\n- ')}`,
    `Then run build ("${cfg.commands.build}") and tests ("${cfg.commands.test}").`,
    `Commit with subject "<type>(<scope>): <desc>" and trailer lines:\n` +
    `Task ${task.id} from ${cfg.planPath}\nPlan-SHA: ${cfg.planSha}\nBase-SHA: ${cfg.baseSha}`,
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
    await runParallelGroup(group)
  }
  const gateTask = group.find(t => t.milestoneEnd)
  if (gateTask) await reviewGate('breakpoint', `milestone after task ${gateTask.id}`)
}

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
      `run branch "${cfg.branch}" (merge commit; NEVER reset --hard, NEVER force-push), ` +
      `resolve conflicts favouring already-merged lanes, then run ` +
      `"${cfg.commands.build}" and "${cfg.commands.test}" on ${cfg.branch}. ` +
      `Return status done only if both pass after the merge.`,
      { schema: TASK_RESULT, phase: 'Tasks', label: `merge:task-${task.id}` })
    if (merge?.status !== 'done') {
      throw new Error(`Merge of task ${task.id} lane failed: ${merge?.failure ?? 'no result'}. ` +
        `All lane branches are preserved; resolve manually and resume.`)
    }
  }
  log(`Group merged: build+test green on ${cfg.branch} after each lane`)
}

async function gateFindings(rawFindings, where) {
  const findings = (rawFindings ?? []).map(f => ({ ...f, where, status: 'open' }))

  for (const f of findings) {
    const blocking = f.severity === 'critical' || f.severity === 'major'
    if (!blocking) { state.findings.push(f); continue }
    if (cfg.flags?.acceptRisk?.includes(f.id)) { f.status = 'accepted-risk'; state.findings.push(f); continue }
    const maxCycles = cfg.flags?.maxFixCycles ?? 3
    for (let cycle = 1; cycle <= maxCycles && f.status !== 'fixed'; cycle++) {
      spendRetry(`fix ${f.id} cycle ${cycle}`)
      const fix = await agent(
        `Fix review finding ${f.id} (${f.severity}) at ${f.file}${f.line ? ':' + f.line : ''}: ` +
        `${f.summary}\nSuggested fix: ${f.fix ?? 'none given'}\n` +
        `Make the minimal correct change, run build ("${cfg.commands.build}") and ` +
        `tests ("${cfg.commands.test}"), then commit with subject ` +
        `"review(${where}): fix ${f.id} — <summary>" and trailer "Plan-SHA: ${cfg.planSha}". ` +
        `NEVER include a "Task N from" footer on a review-fix commit.`,
        { schema: FIX_RESULT, phase: 'Review Gates', label: `fix:${f.id}` })
      if (fix?.status === 'fixed') f.status = 'fixed'
    }
    state.findings.push(f)
  }
  const stillOpen = findings.find(f =>
    f.status === 'open' && (f.severity === 'critical' || f.severity === 'major'))
  if (stillOpen) {
    throw new Error(`Finding ${stillOpen.id} (${stillOpen.severity}) still open after fix cycles at ${where}. ` +
      `Re-run with acceptRisk including "${stillOpen.id}" to accept, or fix manually and resume.`)
  }
  log(`${where}: ${findings.length} finding(s) — ` +
      `${findings.filter(f => f.status === 'fixed').length} fixed, ` +
      `${findings.filter(f => f.status === 'accepted-risk').length} accepted-risk, ` +
      `${findings.filter(f => f.status === 'open').length} open (non-blocking)`)
  return findings
}

async function reviewGate(profile, where) {
  const range = `${cfg.baseSha}..HEAD`
  const reviewPrompt = profile === 'breakpoint'
    ? `Run the built-in /code-review skill at medium effort on the diff ${range} ` +
      `(exclude ${cfg.planPath} and docs/decisions/**). Intent: ${plan.intent}. ` +
      `Return every finding as structured output.`
    : `Invoke the domain-review skill (Skill tool) with profile: full on the diff ` +
      `${range} (exclude ${cfg.planPath} and docs/decisions/**), ` +
      `pr_description: "${plan.intent}". Return its merged findings as structured output.`
  const review = await agent(reviewPrompt,
    { schema: FINDINGS_SCHEMA, phase: 'Review Gates', label: `review:${where}` })
  return gateFindings(review?.findings ?? [], where)
}

// ---------- Phase: Review Gates (PR boundary) ----------
phase('Review Gates')
const checkpoint = await agent(
  `Final quality gate on branch ${cfg.branch}: run lint ("${cfg.commands.lint}"), ` +
  `build ("${cfg.commands.build}"), tests ("${cfg.commands.test}"). If the diff ` +
  `${cfg.baseSha}..HEAD touches product source (not just tests/docs/config), also ` +
  `invoke the built-in /verify skill to exercise the changed flow end-to-end. ` +
  `Report any lint, build, test, or /verify failures as findings: severity 'critical' ` +
  `for a broken build or failing tests, severity 'major' for a lint or /verify failure. ` +
  `Return an empty findings array if everything passed.`,
  { schema: FINDINGS_SCHEMA, label: 'checkpoint' })
if (!checkpoint) throw new Error('Checkpoint agent failed to return a result')
await gateFindings(checkpoint.findings ?? [], 'checkpoint')

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
  `Plan-alignment check: re-read ${cfg.planPath}, compare against the diff ` +
  `${cfg.baseSha}..HEAD. Verify every task is implemented as specified. List every ` +
  `unplanned change as a deviation, classifying per these canonical categories: ` +
  `lockfile (only lock files changed), dep-patch-bump (semver patch-only version ` +
  `bump), formatter (whitespace/quotes only, no AST change — if unsure it does NOT ` +
  `qualify), auto-generated-files, else unmatched.`,
  { schema: DEVIATIONS_SCHEMA, label: 'plan-alignment' })
const AUTO_ACCEPT = ['lockfile', 'dep-patch-bump', 'formatter', 'auto-generated-files']
for (const d of alignment?.deviations ?? []) {
  d.status = AUTO_ACCEPT.includes(d.category) ? 'disagree-with-evidence'
    : cfg.flags?.acceptRisk?.includes(d.id) ? 'accepted-risk' : 'open'
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
if (cfg.flags?.adversarial === 'always' || (cfg.flags?.adversarial === 'auto' && bigDiff)) {
  const adv = await agent(
    `Invoke the review-adversarial skill on diff ${cfg.baseSha}..HEAD with intent ` +
    `"${plan.intent}". If its cross-model CLIs are unavailable, run the built-in ` +
    `/code-review at high effort instead and say which path you took. Return findings.`,
    { schema: FINDINGS_SCHEMA, label: 'adversarial' })
  adversarial = { status: 'ran', findings: adv?.findings ?? [] }
  await gateFindings(adversarial.findings, 'adversarial')
}

// ---------- Phase: Report ----------
phase('Report')
const blockingOpen = state.findings.filter(f => f.status === 'open' && ['critical', 'major'].includes(f.severity))
const verdict = blockingOpen.length ? 'FAIL'
  : (state.findings.some(f => f.status !== 'fixed') || state.deviations.length) ? 'WARN' : 'PASS'
return {
  schema_version: 1,
  verdict,
  plan_file: cfg.planPath, plan_sha: cfg.planSha,
  base_sha: cfg.baseSha, branch: cfg.branch,
  tasks: state.taskResults,
  findings: state.findings,
  deviations: state.deviations,
  retry_stats: { total_retries: state.retries, budget: MAX_RETRIES },
  adversarial,
  run_started: cfg.timestamp,
}
