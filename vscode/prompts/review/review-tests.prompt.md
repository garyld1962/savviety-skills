---
description: >-
  Test quality review: coverage gaps, behavior-focused testing, proper async
  assertions, test isolation, and meaningful descriptions.
agent: 'ask'
tools:
  - read
  - search
  - codebase
---

# Test Quality Review

Quick review of test code for quality, coverage gaps, and adherence to testing best practices.

---

## CRITICAL: Do Not Guess

- **Test framework**: DETECT which framework (vitest, jest, mocha, etc.) before reviewing. Different frameworks have different assertion patterns, mocking APIs, and lifecycle hooks.
- **Coverage expectations**: Check project docs for coverage requirements. Do NOT assume 80% or any specific threshold.
- **Test file convention**: Check where tests live (colocated, `__tests__/`, `test/`) and what they're named (`*.test.ts`, `*.spec.ts`).
- **Mock patterns**: Check how existing tests mock dependencies. Is it `vi.mock`, `jest.mock`, manual stubs, dependency injection? Match the project.
- **Source file existence**: Before flagging "missing test for X," verify X actually exists by reading the source file.

---

## Step 1: Detect Test Conventions

```bash
# Find test framework
cat package.json | grep -E '"(vitest|jest|mocha|ava|tap)"'
ls vitest.config.* jest.config.* .mocharc.* 2>/dev/null

# Find test files
find . -name '*.test.ts' -o -name '*.spec.ts' | head -10

# Read one test to learn patterns
```

---

## Step 2: Check Each Pattern

### 2a. Coverage Gaps

For each source file in scope, check if a corresponding test file exists:

```bash
# For each changed source file
# src/services/auth.ts → check for src/services/auth.test.ts OR __tests__/auth.test.ts
```

| Check | Pass | Fail |
|-------|------|------|
| Source file has corresponding test file | Test file exists | **No test file** |
| Public functions/methods have tests | Each exported function tested | Untested exports |
| Error paths tested | Tests for failure cases | Only happy path |
| Edge cases covered | Boundary values, empty input, null | Only typical input |

### 2b. Behavior vs Implementation Testing

| Check | Pass | Fail |
|-------|------|------|
| Tests describe behavior, not implementation | "returns user when ID exists" | "calls findById on repository" |
| Tests don't assert internal state | Asserts outputs/effects | Asserts internal variables |
| Tests survive refactoring | Would still pass if implementation changes | Breaks on any internal change |

### Example: Correct (behavior-focused)

```typescript
it('returns the user when given a valid ID', async () => {
  const user = await userService.getById('user-123');
  expect(user.name).toBe('Alice');
});
```

### Example: INCORRECT (implementation-focused)

```typescript
// WRONG: Testing implementation details
it('calls the repository findById method', async () => {
  await userService.getById('user-123');
  expect(mockRepo.findById).toHaveBeenCalledWith('user-123');  // ← fragile
});
```

### 2c. Async Assertions

| Check | Pass | Fail |
|-------|------|------|
| Async tests properly awaited | `await expect(fn()).rejects.toThrow()` | Missing await on async assertion |
| Promise rejections tested | Rejection case covered | Only resolved case |
| Timer-based tests use fake timers | `vi.useFakeTimers()` / `jest.useFakeTimers()` | Real `setTimeout` in tests |

### Example: Correct async assertion

```typescript
// vitest/jest
await expect(userService.getById('invalid')).rejects.toThrow(NotFoundError);
```

### Example: INCORRECT

```typescript
// WRONG: Missing await — test always passes regardless of outcome
expect(userService.getById('invalid')).rejects.toThrow(NotFoundError);
```

### 2d. Test Isolation

| Check | Pass | Fail |
|-------|------|------|
| Tests don't depend on execution order | Each test sets up its own state | Relies on previous test |
| Shared state cleaned up | `beforeEach` resets, mocks restored | Leaked state between tests |
| No file system side effects | Uses temp dirs or mocks | Writes to real fs |
| No network calls | HTTP mocked or stubbed | Real API calls in tests |

### 2e. Test Descriptions

| Check | Pass | Fail |
|-------|------|------|
| `describe` blocks name the unit under test | `describe('UserService')` | `describe('tests')` |
| `it` blocks describe the behavior | `it('returns null when user not found')` | `it('works')`, `it('test1')` |
| Negative cases clearly stated | `it('rejects when...')`, `it('throws when...')` | Unclear negative descriptions |

---

## Step 3: Report

```
## Test Quality Review: <file(s)>

**Framework:** <detected>
**Convention:** <test file pattern and location>

| Pattern | Verdict | Findings |
|---------|---------|----------|
| Coverage | PASS/WARN/FAIL | N gaps found |
| Behavior Focus | PASS/WARN/FAIL | N implementation tests |
| Async Assertions | PASS/WARN/FAIL | N missing awaits |
| Isolation | PASS/WARN/FAIL | N leaked states |
| Descriptions | PASS/WARN/FAIL | N unclear descriptions |

### Findings
1. **[severity]** `file:line` — <description>
   - Expected: <correct test pattern>
   - Found: <what the test does>
   - Fix: <specific change>

### Missing Tests
[List source files without corresponding test files]
```

---

## Rules

1. **Behavior over implementation.** Tests that assert internal method calls are fragile. Flag them.
2. **Async matters.** A missing `await` on an async assertion means the test ALWAYS passes. This is a high-severity finding.
3. **Match the project.** Use the project's mock patterns, assertion style, and file conventions in your recommendations.
4. **Coverage gaps are findings.** An untested public function is at least a medium finding.
5. **Verify before flagging.** Before saying "missing test for X," confirm X exists and is exported.
