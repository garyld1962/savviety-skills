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

const ROUTE_SCHEMA = {
  type: 'object', required: ['available'],
  properties: {
    available: { type: 'boolean' },          // false = jev-gate tool missing or call errored
    error: { type: 'string' },
    selected_lane: { type: 'string' },
    reason: { type: 'string' },
    lane_model: { type: 'string' },          // TriageResult.lane.model (null lane -> omit)
    raw_choice: { type: 'string' },          // decision.answers.coding_lane.choice
    raw_confidence: { type: 'number' },      // decision.answers.coding_lane.confidence
    decision_status: { type: 'string' },     // decision.status: live | mock | degraded
    files: {
      type: 'array',
      items: {
        type: 'object', required: ['path', 'action'],
        properties: {
          path: { type: 'string' },
          action: { type: 'string', enum: ['keep_full', 'keep_signatures_only', 'drop'] },
        },
      },
    },
  },
}

// ---------- shared run state ----------
const MAX_RETRIES = cfg.flags?.maxRetries ?? 20
const state = { retries: 0, taskResults: [], findings: [], deviations: [], routing: [], jevGateDown: false }

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

// ---------- Model routing (jev-gate Contract 3, decided by the orchestrator) ----------
// The coding agent's model is fixed once it is spawned, so the lane decision
// must happen here, before agent(). A cheap Haiku agent calls the jev-gate MCP
// tool (workflow scripts cannot call MCP directly); the policy below is plain
// code so it is deterministic and resumable.
const ROUTING = cfg.flags?.modelRouting ?? 'auto'   // 'auto' | 'off'
const LANE_CONFIDENCE_MIN = cfg.flags?.laneConfidenceMin ?? 0.65
const DEEP_FALLBACK = 'opus'
const MODEL_RANK = { haiku: 0, sonnet: 1, opus: 2 }   // only these are ordered; others never auto-replaced

function modelAlias(modelId) {
  const m = /(fable|opus|sonnet|haiku)/i.exec(modelId ?? '')
  return m ? m[1].toLowerCase() : undefined
}

async function routeTask(task, attempt) {
  if (ROUTING === 'off') return { model: undefined, lane: 'inherit', reason: 'modelRouting=off' }
  if (state.jevGateDown) return { model: DEEP_FALLBACK, lane: 'deep_lane', reason: 'jev-gate unreachable (cached) — deep_lane fallback' }
  const taskPrompt = [`Task ${task.id}: ${task.title}`, task.body,
    `Acceptance:\n- ${task.acceptance.join('\n- ')}`].join('\n\n')
  const r = await agent(
    `You are a router. Do NOT implement anything or edit files.\n` +
    `1. Load the jev-gate tool: ToolSearch query "select:mcp__jev-gate__triage_coding_task". ` +
    `If it is not found, return {available: false, error: "tool not found"}.\n` +
    `2. Expand these write-scope globs to EXISTING repo files with Glob (max 64 paths, ` +
    `repo-relative): ${task.writeScope.join(', ')}.\n` +
    `3. Call triage_coding_task with retry_count=${attempt - 1}, candidate_files = those paths, ` +
    `and task_prompt = the text between the markers, verbatim:\n<<<TASK\n${taskPrompt}\n>>>TASK\n` +
    `4. Copy fields from the tool result exactly: selected_lane, reason, lane.model -> lane_model ` +
    `(omit if lane is null), decision.answers.coding_lane.choice -> raw_choice, ` +
    `decision.answers.coding_lane.confidence -> raw_confidence, decision.status -> decision_status, ` +
    `files[] -> files (path, action). available = true. If the call errors, return ` +
    `{available: false, error: <message>}.`,
    { schema: ROUTE_SCHEMA, model: 'haiku', effort: 'low', phase: 'Tasks', label: `route:task-${task.id}` })
  return decideRoute(r)
}

function decideRoute(r) {
  if (!r?.available || r.decision_status !== 'live') {
    if (r && !r.available) state.jevGateDown = true   // confirmed missing/erroring; a dead router agent is transient
    return { model: DEEP_FALLBACK, lane: 'deep_lane',
      reason: `jev-gate ${r?.available ? 'decision ' + (r.decision_status ?? 'unknown') : 'unreachable'}` +
        `${r?.error ? ' (' + r.error + ')' : ''} — deep_lane fallback` }
  }
  const files = r.files ?? []
  // The server folds low confidence into insufficient_context; separate the two
  // using the raw answer so only a confident abstention halts the task.
  if (r.raw_choice === 'insufficient_context' && (r.raw_confidence ?? 0) >= LANE_CONFIDENCE_MIN) {
    return { halt: true, lane: 'insufficient_context', files,
      reason: `jev-gate abstained (confidence ${(r.raw_confidence ?? 0).toFixed(2)})` }
  }
  const alias = modelAlias(r.lane_model)
  if (r.lane_model && alias && (r.raw_confidence ?? 0) >= LANE_CONFIDENCE_MIN) {
    return { model: alias, lane: r.selected_lane, files,
      reason: `${r.selected_lane} → ${r.lane_model} (confidence ${(r.raw_confidence ?? 0).toFixed(2)})` }
  }
  return { model: DEEP_FALLBACK, lane: 'deep_lane', files,
    reason: `low confidence or unusable lane (${r.reason ?? 'n/a'}; model ${r.lane_model ?? 'none'}) — deep_lane fallback` }
}

function contextGuidance(files) {
  if (!files?.length) return ''
  const by = a => files.filter(f => f.action === a).map(f => f.path)
  const full = by('keep_full'), sigs = by('keep_signatures_only'), drop = by('drop')
  return [
    `Context pruning (decided by jev-gate; follow it):`,
    full.length ? `- Read fully: ${full.join(', ')}` : '',
    sigs.length ? `- Read exported signatures/interfaces only: ${sigs.join(', ')}` : '',
    drop.length ? `- Do not read: ${drop.join(', ')}` : '',
  ].filter(Boolean).join('\n')
}

function implPrompt(task, attempt, priorFailure, route) {
  return [
    `Implement Task ${task.id} ("${task.title}") from ${cfg.planPath}.`,
    `Repo branch: ${cfg.branch}. Follow the plan exactly — no unplanned improvements.`,
    plan.closedDecisions?.length
      ? `Closed decisions (tablestakes — execute as stated, never re-litigate):\n- ${plan.closedDecisions.join('\n- ')}`
      : '',
    `Task spec:\n${task.body}`,
    `Write scope (only these globs): ${task.writeScope.join(', ')}. ${CO_TENANCY}`,
    contextGuidance(route?.files),
    `TDD: if an acceptance bullet names a test that doesn't exist, write it ` +
    `first and see it fail before implementing.`,
    `Acceptance (ALL must pass):\n- ${task.acceptance.join('\n- ')}`,
    `Before running slow builds/tests, if jev-gate MCP is available, pass git diff ` +
    `to verify_code_invariants(git_diff) and fix any violated project invariant from .jev-gate.toml.`,
    `Then run build ("${cfg.commands.build}") and tests ("${cfg.commands.test}").`,
    `Commit with subject "<type>(<scope>): <desc>" and trailer lines:\n` +
    `Task ${task.id} from ${cfg.planPath}\nPlan-SHA: ${cfg.planSha}\nBase-SHA: ${cfg.baseSha}`,
    attempt > 1 ? `Attempt ${attempt}. Prior failure:\n${priorFailure}` : '',
    `Return status done only if acceptance, build, and tests all pass.`,
  ].filter(Boolean).join('\n\n')
}

async function runTask(task, opts = {}) {
  let failure = ''
  let prevModel
  for (let attempt = 1; attempt <= 3; attempt++) {
    if (attempt > 1) spendRetry(`task ${task.id} attempt ${attempt}`)
    const route = await routeTask(task, attempt)
    if (route.halt) {
      state.routing.push({ task: task.id, attempt, ...route })
      return { id: task.id, status: 'blocked', failure: `AMBIGUITY: ${route.reason} — clarify the task spec before re-running.` }
    }
    // Never downgrade on a retry: a failed attempt is evidence the task is harder.
    let model = route.model
    if (prevModel && model in MODEL_RANK && prevModel in MODEL_RANK && MODEL_RANK[model] < MODEL_RANK[prevModel]) {
      route.reason += ` — kept ${prevModel} (no downgrade on retry)`
      model = prevModel
    }
    prevModel = model
    state.routing.push({ task: task.id, attempt, model: model ?? 'inherit', lane: route.lane, reason: route.reason })
    log(`Task ${task.id} attempt ${attempt}: ${model ?? 'session model'} — ${route.reason}`)
    const r = await agent(implPrompt(task, attempt, failure, route),
      { schema: TASK_RESULT, phase: 'Tasks', label: `task:${task.id}`, ...opts, ...(model ? { model } : {}) })
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
  `Final quality gate on branch ${cfg.branch}: first, if the jev-gate MCP server ` +
  `is available, run verify_code_invariants(git_diff) on ${cfg.baseSha}..HEAD (report ` +
  `any violated invariant as severity 'major', or log skipped if jev-gate is unreachable). ` +
  `Then run lint ("${cfg.commands.lint}"), ` +
  `build ("${cfg.commands.build}"), tests ("${cfg.commands.test}"). If the diff ` +
  `${cfg.baseSha}..HEAD touches product source (not just tests/docs/config), also ` +
  `invoke the built-in /verify skill to exercise the changed flow end-to-end. ` +
  `Report any invariant, lint, build, test, or /verify failures as findings: severity 'critical' ` +
  `for a broken build or failing tests, severity 'major' for an invariant, lint, or /verify failure. ` +
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
  routing: state.routing,
  findings: state.findings,
  deviations: state.deviations,
  retry_stats: { total_retries: state.retries, budget: MAX_RETRIES },
  adversarial,
  run_started: cfg.timestamp,
}
