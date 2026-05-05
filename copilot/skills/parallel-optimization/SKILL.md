---
name: parallel-optimization
description: >
  Analyzes a PRD or draft execution plan and produces a parallel-agent execution
  map with dependency barriers, write scope assignments, and task ownership for
  safe concurrent execution. Use this before execute-plan or execute-prd when
  tasks can be distributed across specialist agents via /fleet. Not for
  single-package changes where parallelism cannot help, or when the plan already
  has a Parallel Execution section that does not need updating.
---

# parallel-optimization

Purpose: turn requirements into a concurrency-safe execution map. The
output is not a separate source of truth; it is a required section
embedded in the execution plan that later governs execute-plan.

## When to Use

- Inside execute-prd, after the plan is drafted and before
  validate-plan runs.
- When converting a sequential plan to a parallel one, before re-running
  execute-plan.
- When optimizing task ownership for a monorepo with disjoint package
  boundaries.

## When NOT to Use

- Single-package change where parallelism cannot help.
- The plan already has a `## Parallel Execution` section and you are
  not changing it — execute-plan reads it as-is.

## Inputs

Read only the artifacts needed for the planning pass:

1. Repo instructions and command contract (`copilot-instructions.md ## Commands`).
2. The PRD or draft execution plan.
3. Existing package/module layout, if present.
4. Existing tests and manifests, if present.

## Analysis

Classify each work item by:

- **Write scope:** exact file paths or globs the worker may edit.
- **Dependencies:** contracts, generated files, schema, types, APIs, or
  tests that must exist first.
- **Shared-surface risk:** root manifests, lockfiles, shared exports,
  schemas, migrations, generated files, public API contracts, or
  cross-package config.
- **Verification:** the narrow command that proves the slice works.
- **Integration owner:** the lane responsible for root commands,
  lockfile conflict resolution, and final gates.

Prefer package/module boundaries over feature slices when they produce
disjoint write scopes. Do not parallelize work that naturally edits the
same files unless one lane is read-only.

## Safe Parallel Conditions

A plan is parallel-safe only when all applicable conditions are true:

- Lanes have disjoint write scopes, or the overlap is explicitly
  assigned to one owner.
- Root manifests, lockfiles, shared type exports, public contracts,
  migrations, and generated files have a single owner.
- Contract-producing tasks run before contract-consuming tasks.
- Each lane has focused verification commands, not only repo-wide gates.
- Milestone barriers exist where downstream lanes must wait for shared
  contracts, schemas, or APIs.
- The main executor owns integration, final lint/build/test, and
  conflict resolution.
- Specialist agent instructions say they are not alone in the codebase
  and must not revert other agents' edits.

If these conditions cannot be met, emit a sequential plan and state why
parallelism is unsafe.

## Required Plan Section

Add this section to the generated or optimized plan:

```markdown
## Parallel Execution

**Mode:** parallel | sequential
**Rationale:** <one or two sentences>

### Shared Context Packet
- <repo commands, invariants, contracts, and closed decisions every agent needs>

### Ownership
| Lane | Agent type | Tasks | Write scope | Shared-surface owner | Dependencies | Verification |
|---|---|---|---|---|---|---|
| foundation | specialist | 1-2 | package.json, tsconfig.base.json, packages/shared/** | yes | none | pnpm --filter ... |

### Barriers
| Barrier | Wait for | Then unblock |
|---|---|---|
| contracts-ready | shared exports and schemas build | db, api, web lanes |

### Single-Owner Files
- `package.json`: foundation
- `pnpm-lock.yaml`: integration

### Parallel Safety Checks
- [ ] Disjoint write scopes or explicit owner for overlap
- [ ] Shared/public contracts produced before consumers
- [ ] Focused verification per lane
- [ ] Integration lane owns final root gates
- [ ] Specialist agent prompts include multi-agent coordination warning
```

Keep the table concrete. Avoid vague scopes such as "backend files"
when a package path can be named.

## Relationship to Copilot Built-ins

- `/fleet` is the built-in that dispatches work to parallel specialist agents.
  The Parallel Execution section produced by this skill is consumed directly
  by /fleet to determine lane topology and barrier sequencing.
- `/tasks` tracks long-running per-lane commands (build, test, lint). Each
  lane's verification command should be registered with /tasks.
- execute-plan and execute-prd read the Parallel Execution section; do not
  duplicate it across multiple plan files.

## Output Rules

- Preserve the PRD's product requirements; optimization may reorder
  tasks but must not drop acceptance criteria.
- Use milestone barriers instead of waiting after every task.
- Keep root setup, shared contracts, and final verification centralized
  unless the repo already has strong package isolation.
- For greenfield work, create contracts first, then run DB/API/Web
  lanes in parallel when write scopes are separate.
- For existing repos, audit before assigning lanes; parallelize only
  after overlapping files are known.

## Things you must not do

- Do not propose parallelism when write-scope overlap cannot be
  resolved by single-owner assignment. Emit `Mode: sequential` and
  state why.
- Do not rewrite product requirements. Optimization is concurrency
  shape, not scope.
- Do not duplicate the section in multiple plan files. The plan
  execute-plan consumes is the only source.
