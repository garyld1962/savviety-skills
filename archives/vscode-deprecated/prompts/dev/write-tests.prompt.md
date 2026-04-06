---
description: >-
  Write tests for existing code. Detects test framework and patterns from the
  project, then generates tests that match. Not a test plan — actually writes
  test files.
argument-hint: '<file or function to test>'
agent: 'agent'
tools:
  - execute
  - read
  - search
  - codebase
  - edit
---

# Write Tests — Test Generation Grounded in Project Patterns

Generate tests that match the project's existing test style. Read patterns first, then write.

## When to Use

- "Write tests for this file / function / service"
- "Add test coverage for this area"
- "This code has no tests — add them"
- After implementing a feature that needs tests

---

## CRITICAL: Do Not Guess

- **Test framework**: DETECT it. Do NOT assume vitest, jest, xunit, or anything else. Check config files and existing tests.
- **Test file location**: Check where existing tests live. Same directory? `__tests__/`? `tests/`? Match the project.
- **Test file naming**: Is it `*.test.ts`, `*.spec.ts`, `*.Tests.cs`? Match existing.
- **Assertion style**: Does the project use `expect().toBe()`, `assert.equal()`, `Assert.That()`? Read an existing test.
- **Mocking approach**: Does the project mock with `vi.mock`, `jest.mock`, `Substitute.For<T>()`, or something else? Do NOT introduce a mocking library the project doesn't use.
- **Imports in tests**: Copy import patterns from existing test files. Path aliases, test utilities, custom matchers — they vary by project.

---

## Step 1: Read the Code Under Test

### 1a. Read the target file completely

Understand every exported function/class/method:
- What are the inputs and their types?
- What are the outputs?
- What side effects exist? (DB calls, API calls, file writes, events)
- What error conditions exist?
- What edge cases are there? (empty input, null, max values, concurrent access)

### 1b. Read its dependencies

What does the target import? For each dependency:
- Is it a project module (might need mocking)?
- Is it an external library (usually don't mock)?
- Is it a type-only import (no need to mock)?

---

## Step 2: Learn the Test Patterns

### 2a. Detect test framework

```bash
# Check for test config files
ls vitest.config.* jest.config.* .mocharc.* 2>/dev/null

# Check package.json for test dependencies
cat package.json | grep -E '"(vitest|jest|mocha|@jest|@testing-library)"'

# For .NET
ls *.Tests.csproj *Tests/*.csproj 2>/dev/null
```

### 2b. Read 2-3 existing test files

Find tests near the target file or in the same package:

```bash
# Search for existing tests
```

From these files, extract:
```
Test framework: <detected>
File naming: <e.g., *.test.ts, *.spec.ts>
File location: <same dir, __tests__, tests/>
Import patterns: <how tests import the code under test>
Setup pattern: <beforeEach, beforeAll, factory functions, or none>
Mocking: <vi.mock, jest.mock, manual mocks, DI, or none>
Assertion style: <expect/toBe, assert, Assert.That>
Describe/test structure: <nested describes, flat tests, test classes>
```

**If NO test files exist in the project:** Tell the user and ask which framework to use before proceeding.

---

## Step 3: Write Tests

### Structure

Match the structure from existing tests. Typical patterns:

```typescript
// Pattern A: Flat tests (common in service/utility code)
describe('functionName', () => {
  test('returns X when given Y', () => { ... });
  test('throws when given invalid input', () => { ... });
});

// Pattern B: Nested describes (common for classes/complex services)
describe('ClassName', () => {
  describe('methodName', () => {
    test('happy path', () => { ... });
    test('error path', () => { ... });
  });
});
```

### What to test

For each exported function/method, cover:

1. **Happy path** — typical valid input produces expected output
2. **Edge cases** — empty input, boundary values, special characters
3. **Error paths** — invalid input, missing dependencies, failure conditions
4. **Return values** — assert on the actual return, not on implementation details

### What NOT to test

- Private functions (test them through their public callers)
- Framework behavior (don't test that Express routes or React renders)
- Type system (TypeScript already checks this at compile time)
- Trivial code (pure data objects, simple getters)

### Mocking discipline

- Mock EXTERNAL boundaries (database, HTTP, file system, message queues)
- Do NOT mock the code under test
- Do NOT mock internal utility functions unless they have side effects
- Prefer dependency injection over global mocks when the project supports it
- Use the project's existing mocking patterns — do NOT introduce new ones

---

## Step 4: Verify

### 4a. Tests run

```bash
<detected-test-command>
```

### 4b. Tests pass

If tests fail:
1. Read the error — is it a real bug in the code, or a test error?
2. If test error: fix the test
3. If real bug: note it in the report (do NOT fix the production code)
4. Retry (max 3 attempts for test errors)

### 4c. No test pollution

Verify tests clean up after themselves (close connections, reset mocks, restore state).

---

## Step 5: Report

```
## Tests Written

**Target:** <file or function tested>
**Test file:** <path to new test file>
**Framework:** <detected>

**Coverage:**
| Function/Method | Happy Path | Edge Cases | Error Paths |
|----------------|------------|------------|-------------|
| functionName   | YES        | YES        | YES         |

**Tests: N total, N passing**

**Notes:**
- <any bugs discovered during testing>
- <any areas that need integration tests instead of unit tests>
```

---

## Rules

1. **Read existing tests first.** Your tests must be stylistically identical to the project's existing tests.
2. **Test behavior, not implementation.** Assert on outputs and side effects, not on how the code internally works.
3. **One assertion per test.** Each test should verify one thing. "It works" is not a test description.
4. **Meaningful names.** `'returns 400 when email is missing'` not `'test1'` or `'it works'`.
5. **No new dependencies.** Use only the test framework and utilities already in the project.
6. **If a test reveals a bug, report it — don't fix it.** The test file is the deliverable, not a bug fix.
