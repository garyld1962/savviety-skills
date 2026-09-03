---
name: test-plan
description: Use before implementing a feature to generate it.todo() stubs from requirements
  (TDD-first). Supports plan, validate, and refresh modes. TypeScript monorepos.
whenToUse: Use before implementing a feature to generate it.todo() stubs from requirements
  (TDD-first). Supports plan, validate, and refresh modes. TypeScript monorepos.
type: flow
disableModelInvocation: false
arguments:
- task
---


# /skill:test-plan — TDD-First Test Planning

**Purpose:** Generate test specifications from task requirements BEFORE implementation. Tests serve as executable specifications that define what the code must do. Designed for iterative use by team agents in a TDD workflow. Project-agnostic — adapts to any TypeScript monorepo.

## When to Use

- Starting TDD on a new task — generate `it.todo()` stubs before implementation
- Validating whether an existing test suite covers the task requirements
- Refreshing a plan after requirements change

## When NOT to Use

- Implementation already exists and passes — use `/review-tests` to audit coverage
- Non-TypeScript repo without an equivalent test runner convention
- Exploratory spike code that will be discarded

## Test Philosophy

**Tests should verify behavior through public interfaces, not implementation details.** Code can change entirely; tests shouldn't break.

Good tests exercise real code paths through public APIs and describe *what* the system does. A good test reads like a specification — "user can checkout with valid cart." These survive refactors because they don't care about internal structure.

Bad tests are coupled to implementation: they mock internal collaborators, test private methods, or assert on call counts. The warning sign: your test breaks when you refactor but behavior hasn't changed.

```typescript
// Good — tests observable behavior through the interface
test("createUser makes user retrievable", async () => {
  const user = await createUser({ name: "Alice" });
  const retrieved = await getUser(user.id);
  expect(retrieved.name).toBe("Alice");
});

// Bad — bypasses the interface to verify internals
test("createUser saves to database", async () => {
  await createUser({ name: "Alice" });
  const row = await db.query("SELECT * FROM users WHERE name = ?", ["Alice"]);
  expect(row).toBeDefined();
});
```

**Anti-pattern: horizontal slices.** Do NOT implement all `it.todo()` stubs in bulk, then fill them in. That's "RED all, GREEN all" — it produces tests that verify imagined behavior, test data shapes instead of capabilities, and go stale quickly.

```
WRONG (horizontal):  todo → todo → todo → todo → impl → impl → impl → impl
RIGHT (vertical):    todo → impl → todo → impl → todo → impl
```

Work through stubs one at a time: write the minimal implementation to pass one test, then move to the next.

**Mocking:** Mock at system boundaries only — external APIs, third-party services, time, randomness. Never mock your own modules or internal collaborators. Prefer real substitutes (PGLite for Postgres, in-memory filesystem) over mocks where they exist.

## Implementation Cycle Checklist

Before moving from one stub to the next, verify:

```
[ ] Test describes behavior, not implementation
[ ] Test uses public interface only
[ ] Test would survive an internal refactor
[ ] Implementation is minimal for this test
[ ] No speculative features added
```

After all stubs pass, check for refactor candidates:
- Extract duplication
- Deepen modules (move complexity behind simpler interfaces)
- Apply SOLID where it emerges naturally — never anticipate it

**Never refactor while RED.** Get to GREEN first, always.

## Usage

```
/skill:test-plan --task="Implement vendor CRUD service"   # Plan + generate test files
/skill:test-plan --task="..." --ontology docs/prds/vendors/ONTOLOGY.md   # Use an explicit ontology
/skill:test-plan --validate                                # Run tests, report pass/fail
/skill:test-plan --refresh                                 # Update plan after implementation changes
```

## Modes

### Full Plan (default — `--task="..."`)

Runs the complete orchestrator FSM. Produces test files with `it.todo()` stubs, a plan JSON file, and a markdown report. Use when starting a new feature.

### Validate (`--validate`)

Runs generated test files and reports results:
- Reads `.test-plan/plan-latest.json` to find generated test files
- Executes tests via Vitest: `pnpm vitest run --reporter=json {files}`
- Updates plan with pass/fail/todo counts
- Does NOT regenerate test files or write a new markdown report

### Refresh (`--refresh`)

Re-analyzes the task after implementation changes:
- Reads current implementation to discover new patterns and changed signatures
- Updates specs for evolved code
- Generates updated test files
- Archives old plan, writes new `plan-latest.json` and markdown report

### Ontology input (`--ontology <path>`)

Optional in every mode. Points at an `ONTOLOGY.md` whose format is defined in
`_internal/ontology-readiness/SKILL.md`. When one resolves, its settled rows
become the primary source of test specs and prose re-derivation becomes the
fallback.

**Default resolution when the flag is omitted:**

1. The sibling `ONTOLOGY.md` of the requirements artifact, when the task names
   one or one is discoverable (`docs/prds/<slug>/PRD.md` →
   `docs/prds/<slug>/ONTOLOGY.md`).
2. Otherwise the most recently modified `docs/prds/*/ONTOLOGY.md`.
3. Otherwise none — analysts re-derive constraints from prose exactly as they
   do today. Absence of an ontology is not an error and never `BLOCKED`.

Only rows whose `Status` column reads `settled` are used. `deferred` and
`unknown` rows are ignored with a logged note in the report naming the row and
its state — see `_internal/ontology-readiness/SKILL.md` `### Item states`. An
unsettled row is an open decision, not a test target.

## Project Discovery (Run Once at Start)

Before entering the FSM, load project context:

1. **Read `CLAUDE.md`** from repo root — learn project conventions, error handling, shared package, test framework
2. **Read `.test-plan/config.json`** if it exists — get team mappings, analyst overrides (see `foundations/project-config.md`)
3. **Read workspace config** — `pnpm-workspace.yaml` or root `package.json` `workspaces` field to discover package boundaries
4. **Identify shared package** — from config `sharedPackage` field, or auto-detect

This context is passed to every analyst.

## Orchestrator FSM (7 States)

### State 1: DISCOVER_ASK

Parse the task description to understand what's being built.

**Inputs:** `--task` argument, current branch name, agent prompt (if team agent)

**Extract:**
- **Entity**: The primary domain entity (vendor, rfi, task, change-order)
- **Package**: Target package (packages/api, packages/db, apps/web)
- **Layer**: Target layer (service, router, schema, component)
- **Operations**: What operations are being built (CRUD, transitions, calculations)

**Layer detection:** Use the task description first. If ambiguous, use file path patterns from `.test-plan/config.json` `layerDetection` field, or defaults:
- `**/services/**` → service
- `**/routers/**` → router
- `**/schema/**` → schema
- `**/*.tsx` → component

**For `--validate` mode:** Skip. Read existing plan from `.test-plan/plan-latest.json`.

**For `--refresh` mode:** Read existing plan, then re-parse to find changes.

### State 2: GATHER_CONTEXT

Read all relevant source files to build the specification context.

**Read in order:**
0. **`ONTOLOGY.md`** — the path from `--ontology`, or the default resolution in
   `## Modes` above. Read it first when one resolves: its settled rows
   constrain how every schema below is interpreted. Parse `## Entity Types`
   (reference schemes), `## Fact Types` (Constraints and Modality),
   `## Lifecycles` (Total flag and transition rows), and `## Temporality`.
   Keep each row's `Status`; drop anything that is not `settled` and log it.
1. **Validation schemas** from the project's shared/types package for the target entity — input schemas, output types, enums
2. **DB schema** from the database package for the target entity — columns, types, defaults, relations, status enums
3. **Enum definitions** from the shared package — status values, categories
4. **Reference implementation** — find an existing service/router for a similar entity to learn the established patterns
5. **CLAUDE.md conventions** — error handling patterns, logging, boundary rules, testing expectations

6. **Classify dependencies** using `_internal/dependency-classification/SKILL.md`.

   For each dependency in scope of the target, record `<name> — <category> — <chosen test approach>` in the plan output. Flag miscategorizations (e.g., Postgres mocked rather than substituted with PGLite) as findings. Never mock in-process or local-substitutable dependencies — the rubric explains why.

**Ontology slicing.** When step 0 produced an ontology, split its settled rows
into one slice per analyst. A row may land in more than one slice; a row that
lands in none is carried into the report as unsliced context.

| Ontology rows | Selector | Slice goes to |
|---|---|---|
| `## Fact Types` rows | Constraints cell names a value domain — `value domain: …` is the prefix `/skill:prd-create` emits, and a free-text range or enumeration in the cell without that prefix is still recognised | boundary-validation |
| `## Lifecycles` sections (heading with its `Total:` flag, transition rows, `Terminal:` line) | any lifecycle for an in-scope entity | state-lifecycle |
| `## Fact Types` rows | Constraints cell declares uniqueness, a mandatory role, or fact-type arity | contract-compliance |
| `## Fact Types` rows **plus the `## Entity Types` rows (reference schemes) of every entity those fact types name** | the fact crosses a system edge — an entity on one side is external, or the fact is exchanged over an API | integration-surface |

Each slice is a verbatim copy of the matching rows with their `#` or heading, so
the analyst can cite the row a spec came from. The integration-surface slice is
the only one that carries rows from two sections: its edge-crossing fact-type
rows travel with the `## Entity Types` row of every entity they name, so the
analyst has each entity's reference scheme alongside the fact.

**For `--validate` mode:** Skip. Context already in plan file.

### State 3: SELECT_ANALYSTS

Choose which analysts to run based on the target layer:

| Target Layer | Analysts |
|-------------|----------|
| service | contract-compliance, state-lifecycle, boundary-validation, integration-surface |
| router | contract-compliance, boundary-validation, integration-surface |
| schema | contract-compliance, boundary-validation |
| component | contract-compliance, boundary-validation, integration-surface |

Check `.test-plan/config.json` `analysts` field for overrides (enabled/disabled).

**State-lifecycle exception:** Include `state-lifecycle` if the entity has a
status enum, **or** if the ontology declares a `## Lifecycles` section for the
target entity — an ontology-declared lifecycle selects the analyst even when no
status enum exists in code yet, and its specs then define the enum the
implementation must add. If neither holds, skip even for service layer.

**For `--validate` mode:** Skip. Analysts determined by existing plan.

### State 4: DISPATCH_ANALYSTS

For each selected analyst:
1. Read `test-plan/analysts/{name}/SKILL.md`
2. Pass the task context, Zod schemas, DB schema, reference implementation, and CLAUDE.md conventions
3. Pass that analyst's **ontology slice** from State 2, when an ontology
   resolved — for integration-surface that is the edge-crossing `## Fact Types`
   rows plus the `## Entity Types` rows (reference schemes) of every entity
   those fact types name. Omit the item when no ontology resolved or the
   analyst's slice is empty — the analyst then re-derives from prose as before.
4. Analyst produces `TestSpecification[]` conforming to the canonical
   schema in `foundations/test-case-schema.md`. Specs that violate the
   schema are dropped at State 5 with a warning — the analyst is
   responsible for valid output.

Analysts run conceptually in parallel — each operates on the same context independently.

**Analyst unavailable / disabled:** If `.test-plan/config.json`
disables a selected analyst, skip it with a logged note in the
report. The plan is still produced from the remaining analysts; the
verdict downgrades to `PARTIAL` if the missing analyst would have
contributed P1 specs.

**For `--validate` mode:** Skip. Specifications already in plan file.

### State 5: CONSOLIDATE_PLAN

Merge analyst outputs into a unified plan:

0. **Validate against schema**: drop any spec that violates
   `foundations/test-case-schema.md`. Record the count and reason in
   the report; do not silently keep malformed specs.

1. **Deduplicate**: If two analysts produced specs for the same behavior (same testFile + describeBlock + similar testName), keep the higher-priority one. If same priority, keep the one with more assertions. Conflict resolution is fully defined here — analysts do not coordinate.

2. **Assign to test files**: Group specs by `testFile` path. Each unique path becomes one generated file.

3. **Calculate summary**: Count totals by priority, analyst, and category.

4. **Determine verdict**:
   - **READY**: All P1 specs generated, context was complete
   - **PARTIAL**: P1 specs generated but some context was missing (e.g., no Zod schema found)
   - **BLOCKED**: Critical context missing (no entity found, no schemas, can't determine layer)

**For `--validate` mode:** Skip. Proceed to running tests.

### State 6: GENERATE_OUTPUT

#### Full/Refresh Mode

1. **Generate test files**: Pass grouped specs to the test writer (see `test-writer/SKILL.md`). The test writer creates `.test.ts` files with `it.todo()` stubs.

2. **Write plan JSON**: Write `.test-plan/plan-latest.json` conforming to `foundations/plan-schema.md`.
   - Archive existing `plan-latest.json` to `plan-{planId}.json` first (if exists)

3. **Write markdown report**: Use template from `foundations/report-template.md`. Save to `docs/test-plans/`.

4. **Update report index**: Prepend to `docs/test-plans/index.md`. Update `docs/test-plans/latest.md`.

#### Validate Mode

1. **Run tests**: Execute generated test files:
   ```bash
   pnpm vitest run --reporter=json {test-file-paths}
   ```

2. **Parse results**: Count passed, failed, todo tests.

3. **Calculate validation verdict**:
   - **ALL_PASS**: All non-todo tests pass
   - **PARTIAL_PASS**: Some pass, some fail
   - **FAILING**: >50% of non-todo tests fail

4. **Update plan**: Add `validation` field to `.test-plan/plan-latest.json`. Bump timestamp.

### State 7: RESPOND

Present summary to the caller.

#### Full/Refresh Mode Response

```
Test Plan: {entity}.{layer} — {verdict}

Task: "{task description}"
Analysts: {list}

Specs: {total} ({p1} P1, {p2} P2, {p3} P3)

Generated files:
  {path} — {testCount} tests ({todoCount} todos)

Plan: .test-plan/plan-latest.json
Report: {reportPath}

Next steps:
  1. Review generated test files
  2. Implement the feature, making tests pass in P1 → P2 → P3 order
  3. Run /skill:test-plan --validate when ready
```

#### Validate Mode Response

```
Test Plan Validation: {entity}.{layer} — {validation verdict}

Results: {passed} passed, {failed} failed, {todo} todo

{If FAILING: list failed tests with error messages}

Plan updated: .test-plan/plan-latest.json

Next steps:
  {ALL_PASS: "Proceed to /skill:domain-review"}
  {PARTIAL_PASS: "Fix failing tests, then re-validate"}
  {FAILING: "Major implementation issues — review failing tests"}
```

**Critical:** Always include the plan file path in your response. The calling team agent needs this to track progress.

## Team Agent Integration

This skill is designed for TDD use by team agents. The typical lifecycle:

```
task received → /skill:test-plan --task="..."    (generate specs)
implementing  → fill in it.todo() stubs   (TDD)
"done"        → /skill:test-plan --validate      (verify tests pass)
refactored    → /skill:test-plan --refresh       (update specs)
passing       → /skill:domain-review               (quality check)
clean         → create PR
```

See `foundations/team-agent-protocol.md` for the complete workflow.

## Integration with Code Review

The test-plan and domain-review skills are complementary:

| Skill | When | What |
|-------|------|------|
| `/skill:test-plan` | Before implementation | Defines what the code SHOULD do |
| `/skill:domain-review` | After implementation | Verifies how the code IS written |

Both must pass before creating a PR. See `foundations/team-agent-protocol.md` for the combined workflow.

## Relationship to /skill:execute-plan and /skill:execute-prd

`/skill:execute-plan` verifies each task's acceptance criteria and reports coverage holes as `unproved` rows in its final report. It does NOT call `/skill:test-plan`.

Run `/skill:test-plan` manually before invoking `/skill:execute-plan` when you want stronger TDD discipline: analyst-generated specs, classified dependency handling, and `it.todo()` stubs that pre-declare the behavior coverage. The stubs then feed directly into execute-plan's coverage tracking — a test that was generated by `/skill:test-plan` and passes is unambiguously proved.

If you skip `/skill:test-plan`, execute-plan still verifies acceptance criteria per task but without the upfront spec generation. This is fine for straightforward features; use `/skill:test-plan` first when the behavior surface is complex or when `unproved` rows on the final report are unacceptable.

## Relationship to native skills

This skill generates the stubs that superpowers:test-driven-development's red phase consumes; invoke it from within that process, not instead of it.

## Contract

- **Inputs:** task description and target entity name; optional `.test-plan/config.json` (analyst overrides, team mappings, paths); optional `--ontology <path>` (an `ONTOLOGY.md` in the format defined by `_internal/ontology-readiness/SKILL.md`, defaulting to the requirements artifact's sibling then the most recently modified `docs/prds/*/ONTOLOGY.md`); Zod schemas, DB schema, reference implementation, CLAUDE.md conventions. Calls each `test-plan/analysts/<name>/SKILL.md` selected by State 3 and `test-plan/test-writer/SKILL.md` in State 6. Spec schema canonical at `test-plan/foundations/test-case-schema.md`.
- **Preconditions:** TypeScript monorepo with a Vitest-shaped test convention; `foundations/*` files readable; `.test-plan/` directory writable; entity exists in repo (DB and Zod schemas locatable).
- **Outputs:** `.test-plan/plan-latest.json` (conforming to `foundations/plan-schema.md`); markdown report under `docs/test-plans/` (per `foundations/report-template.md`); `.test.ts` files with `it.todo()` stubs from `test-writer` (does not overwrite existing files).
- **Postconditions:** plan verdict is `READY`, `PARTIAL`, or `BLOCKED`; existing tests are preserved; index `docs/test-plans/index.md` and `latest.md` updated.
- **Failure modes:** no ontology resolves → analysts re-derive from prose, plan proceeds (not an error); `deferred` / `unknown` ontology rows → ignored with a logged note naming the row and its state, per `_internal/ontology-readiness/SKILL.md` `### Item states`; critical context missing (no entity / schemas / layer) → `BLOCKED`; analyst disabled in `.test-plan/config.json` → continue and downgrade to `PARTIAL` if its P1s are missed; spec violating canonical schema → drop at State 5 with a logged note (do not silently keep).
