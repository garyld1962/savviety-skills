---
description: >-
  TDD-first test planning: analyze task requirements, generate test specs as
  executable it.todo() stubs BEFORE implementation. Supports plan, validate,
  and refresh modes.
argument-hint: '--task="<description>" | --validate | --refresh'
agent: 'agent'
tools:
  - execute
  - read
  - search
  - codebase
  - edit
---

# TDD-First Test Planning

Generate test specifications from task requirements BEFORE implementation. Tests serve as executable specifications that define what the code must do.

## When to Use

- Starting a new feature — define expected behavior as tests first
- Before implementing a plan task — write failing tests, then make them pass
- After refactoring — refresh specs to match evolved code

## Modes

| Mode | Trigger | What It Does |
|------|---------|-------------|
| **Plan** | `--task="..."` | Full analysis → generate test files with `it.todo()` stubs |
| **Validate** | `--validate` | Run existing tests, report pass/fail/todo counts |
| **Refresh** | `--refresh` | Re-analyze after implementation changes, update specs |

---

## CRITICAL: Do Not Guess

- **Test framework**: DETECT which test framework the project uses. Check `package.json` for vitest, jest, mocha, etc. Do NOT assume vitest.
- **Test file location**: Check existing tests to find the project's test file convention. Is it `__tests__/`, `*.test.ts`, `*.spec.ts`? Do NOT invent a convention.
- **Import paths**: Read actual source files to get correct import paths. Do NOT guess module paths — they vary by project (path aliases, barrel exports, direct file imports).
- **Type names**: Read actual type definitions from the project's shared/types package. Do NOT invent type names, enum values, or schema shapes.
- **Test patterns**: Read an existing test file in the project BEFORE writing new tests. Match the project's test style (describe nesting, setup/teardown, assertion style).
- **API signatures**: Read the actual function/method signature before writing test calls. Do NOT guess parameter names, types, or return types.

---

## Step 1: Project Discovery

Before doing anything, load project context:

### 1a. Find test framework

```bash
# Check package.json for test framework
cat package.json | grep -E '"(vitest|jest|mocha|ava|tape)"'

# Check for test config files
ls vitest.config.* jest.config.* .mocharc.* 2>/dev/null

# Check the test script
cat package.json | grep '"test"'
```

### 1b. Find test conventions

```bash
# Find existing test files to learn the pattern
find . -name '*.test.ts' -o -name '*.test.tsx' -o -name '*.spec.ts' | head -10

# Read one existing test to learn conventions
# (pick the first result from above)
```

**Read at least ONE existing test file** before generating any tests. Note:
- File naming pattern (`*.test.ts` vs `*.spec.ts`)
- Directory structure (colocated vs `__tests__/` vs `test/`)
- Import style (path aliases vs relative)
- Describe/it nesting depth
- Setup/teardown patterns (beforeEach, afterAll, fixtures)
- Assertion style (expect().toBe, assert.equal, etc.)
- Mock patterns (vi.mock, jest.mock, manual stubs)

### 1c. Find shared types

```bash
# Identify the shared/types package
cat pnpm-workspace.yaml 2>/dev/null || cat package.json | grep -A 5 '"workspaces"'

# Find type definitions relevant to the task
grep -r "export type\|export interface\|export enum" packages/shared/src/ --include='*.ts' | head -20
```

### Example: Correct discovery

```
Framework: vitest (from package.json devDependencies)
Config: vitest.config.ts
Pattern: src/**/*.test.ts (colocated)
Style: describe → it, vi.mock for mocking, expect() assertions
Types: packages/shared/src/types.ts
```

### Example: INCORRECT

```
# WRONG: Assuming vitest without checking
import { describe, it, expect } from 'vitest'  # ← Project might use jest
```

---

## Step 2: Parse Task (Plan Mode)

Parse the `--task` argument to extract:

| Field | How to Determine | Example |
|-------|-----------------|---------|
| **Entity** | Primary domain noun in the task | "vendor", "user", "order" |
| **Package** | Directory where implementation will live | "services/api", "packages/web" |
| **Layer** | Code layer being built | service, router, schema, component |
| **Operations** | What the code must do | CRUD, state transitions, calculations |

### Layer detection

Use the task description first. If ambiguous, use file path patterns:

```
**/services/**  → service layer
**/routers/**   → router/API layer
**/schema/**    → data/validation layer
**/*.tsx        → component layer
```

---

## Step 3: Gather Context

Read ALL relevant source files before writing any tests:

### 3a. Validation schemas

```bash
# Search for schemas related to the entity
grep -r "Schema\|z\.object\|z\.string\|z\.number" --include='*.ts' | grep -i "<entity>"
```

Read the actual schema definitions. Note field names, types, and validation rules.

### 3b. Database schema (if applicable)

```bash
grep -r "CREATE TABLE\|model\|@Entity\|@Column" --include='*.ts' --include='*.sql' | grep -i "<entity>"
```

### 3c. Enum/status values

```bash
grep -r "enum\|Status\|State" --include='*.ts' | grep -i "<entity>"
```

### 3d. Reference implementation

Find a similar entity's implementation to learn the project's patterns:

```bash
# Find similar services/routers
find . -path '*/services/*.ts' -not -name '*.test.ts' | head -5
```

**Read at least one reference implementation.** This tells you the function signatures, error handling patterns, and return types your tests need to match.

### Example: Correct context gathering

```
Read: packages/shared/src/schemas/vendor.ts
  → CreateVendorInput schema: { name: string, email: string, category: VendorCategory }
  → VendorCategory enum: ['subcontractor', 'supplier', 'consultant']

Read: services/api/src/services/user.service.ts (reference)
  → Pattern: async method, returns { data, error }, validates input with Zod
```

### Example: INCORRECT

```
# WRONG: Inventing schema without reading it
type CreateVendorInput = { name: string }  # ← Guessed fields
```

---

## Step 4: Select Analysts

Choose which test categories to generate based on the layer:

| Layer | Test Categories |
|-------|----------------|
| Service | Contract compliance, state lifecycle, boundary validation, integration surface |
| Router | Contract compliance, boundary validation, integration surface |
| Schema | Contract compliance, boundary validation |
| Component | Contract compliance, boundary validation, integration surface |

### Category descriptions

| Category | What It Tests | Example |
|----------|-------------- |---------|
| **Contract compliance** | Input validation, output shape, required fields, type correctness | "rejects input missing required 'name' field" |
| **State lifecycle** | Status transitions, valid/invalid paths, terminal states | "cannot transition from 'closed' to 'draft'" |
| **Boundary validation** | Edge cases, limits, empty inputs, max lengths, special characters | "handles empty array input without error" |
| **Integration surface** | API contracts, error responses, auth requirements, response format | "returns 401 for unauthenticated requests" |

**State lifecycle exception:** Only include if the entity has a status/state field. If no status enum exists, skip — do NOT invent lifecycle tests.

---

## Step 5: Generate Test Specifications

For each test category, produce test specifications:

```typescript
// Example: contract-compliance tests for vendor service

describe('VendorService', () => {
  describe('create', () => {
    it.todo('creates a vendor with valid input and returns the created record');
    it.todo('rejects input when required field "name" is missing');
    it.todo('rejects input when "email" format is invalid');
    it.todo('rejects input when "category" is not a valid VendorCategory value');
  });

  describe('getById', () => {
    it.todo('returns the vendor when ID exists');
    it.todo('returns null or throws NotFoundError when ID does not exist');
  });
});
```

### Test specification rules

1. **Use `it.todo()` stubs** — do NOT write full test implementations. The developer fills these in.
2. **One behavior per test** — each `it.todo()` tests exactly one thing.
3. **Descriptive names** — the test name IS the specification. It must be readable without seeing the code.
4. **Match actual types** — use real type names, enum values, and field names from Step 3. Do NOT invent them.
5. **Match actual patterns** — use the project's test style from Step 1b. Do NOT impose a different style.

### Priority assignment

| Priority | What | Examples |
|----------|------|---------|
| **P1** (must have) | Happy path, required validation, type compliance | "creates with valid input", "rejects missing field" |
| **P2** (should have) | Error handling, edge cases, state transitions | "handles database timeout", "empty input array" |
| **P3** (nice to have) | Performance, logging, audit, rare edge cases | "logs creation event", "handles concurrent updates" |

---

## Step 6: Write Output Files

### 6a. Test files

Write `.test.ts` files following the project's naming convention:

```bash
# If project uses colocated tests:
src/services/vendor.test.ts

# If project uses __tests__ directory:
src/services/__tests__/vendor.test.ts
```

Each file includes:
- Correct imports (from the ACTUAL paths discovered in Step 1)
- Describe blocks grouped by method/feature
- `it.todo()` stubs ordered by priority (P1 first)
- Comments indicating priority: `// P1`, `// P2`, `// P3`

### 6b. Plan file

Write `.test-plan/plan-latest.json` with:

```json
{
  "planId": "<8-char-hex>",
  "timestamp": "<ISO 8601>",
  "task": "<original task description>",
  "entity": "<detected entity>",
  "layer": "<detected layer>",
  "verdict": "READY | PARTIAL | BLOCKED",
  "specs": [
    {
      "testFile": "<path>",
      "category": "<analyst>",
      "priority": "P1 | P2 | P3",
      "describePath": ["Service", "create"],
      "testName": "creates vendor with valid input",
      "status": "todo"
    }
  ],
  "summary": {
    "total": 0, "p1": 0, "p2": 0, "p3": 0,
    "byCategory": {}
  }
}
```

### 6c. Markdown report

Write to `docs/test-plans/<date>-<entity>-<layer>.md`:

```markdown
# Test Plan: <entity>.<layer>

**Task:** <description>
**Generated:** <date>
**Verdict:** READY / PARTIAL / BLOCKED

## Specifications

### P1 — Must Have (N tests)
| # | Category | Test | File |
|---|----------|------|------|
| 1 | contract | creates with valid input | src/services/vendor.test.ts |

### P2 — Should Have (N tests)
[table]

### P3 — Nice to Have (N tests)
[table]

## Next Steps
1. Review generated test files
2. Implement the feature, making tests pass in P1 → P2 → P3 order
3. Run validate mode when ready
```

---

## Validate Mode (`--validate`)

1. Read `.test-plan/plan-latest.json`
2. Run tests:
   ```bash
   pnpm vitest run --reporter=json <test-file-paths>
   ```
   **IMPORTANT:** Replace `pnpm vitest` with the project's actual test command from Step 1a. Do NOT assume vitest.
3. Parse results: count passed, failed, todo
4. Report:

```
Test Plan Validation: <entity>.<layer>

Results: N passed, N failed, N todo

[If failures exist: list each with error message]

Next:
  All pass → Proceed to code review
  Some fail → Fix failing tests, re-validate
  Many fail → Review implementation against specs
```

---

## Refresh Mode (`--refresh`)

1. Read existing plan
2. Re-read implementation files (they've changed since initial plan)
3. Update specs for evolved signatures, types, or patterns
4. Archive old plan, write new `plan-latest.json`
5. Regenerate test stubs (add new ones, update changed ones, leave passing tests alone)

---

## Rules

1. **Never write full test implementations.** Generate `it.todo()` stubs only. The developer writes the actual test logic.
2. **Real types only.** Every type, enum, field name, and import path must come from reading actual source files. If you cannot find it, say "COULD NOT FIND — verify manually."
3. **Match project conventions.** Your generated tests must be stylistically indistinguishable from the project's existing tests.
4. **P1 first.** Always generate P1 (happy path + required validation) before P2 and P3.
5. **No phantom tests.** Do NOT generate tests for features, fields, or behaviors that don't exist in the schemas/types. Only test what the code is SPECIFIED to do.
