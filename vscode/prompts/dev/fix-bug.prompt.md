---
description: >-
  Structured bug fix workflow. Reproduces the issue, identifies root cause,
  writes a regression test, then applies the minimal fix. Prevents "try random
  things" debugging.
argument-hint: '<bug description, error message, or file:line>'
agent: 'agent'
tools:
  - execute
  - read
  - search
  - codebase
  - edit
---

# Fix Bug — Structured Debugging and Fix

Find the root cause, write a test that proves the bug exists, fix it minimally, verify the fix.

## When to Use

- Error messages, stack traces, unexpected behavior
- "This endpoint returns 500" / "This function throws" / "This test fails"
- "It used to work but now it doesn't"

---

## CRITICAL: Do Not Guess

- **Root cause**: Do NOT jump to a fix. READ the code path end-to-end first. The bug is often not where it appears.
- **Stack traces**: Read EVERY file referenced in the stack trace. The cause is usually 2-3 frames deep, not at the top.
- **"Obvious" fixes**: If the fix seems obvious without reading the code, you're probably wrong. Read first.
- **Existing tests**: Check if tests exist for this area. If they pass, the bug might be in a different layer than you think.
- **Dependencies**: Verify package versions before blaming a library. `cat package.json | grep '<pkg>'`.
- **Environment**: Check for environment-dependent issues (missing env vars, different Node versions, platform differences) before changing code.

---

## Step 1: Understand the Bug

Parse the bug report. Extract:
- **Symptom**: What actually happens? (error message, wrong output, crash)
- **Expected**: What should happen?
- **Reproduction**: How to trigger it? (endpoint, input, sequence of actions)

If any of these are unclear: ASK. Do NOT fill in gaps with assumptions.

```
Bug: <symptom>
Expected: <correct behavior>
Reproduction: <how to trigger>
```

---

## Step 2: Trace the Code Path

**Do NOT skip this step.** Read the code path from entry point to failure point.

### 2a. Find the entry point

```bash
# Search for the endpoint, function, or handler
# Use actual search — do NOT guess the file
```

### 2b. Follow the execution path

Read each file in the call chain. For each:
- What are the inputs? What types?
- What can go wrong? (null, undefined, empty array, wrong type)
- What does it return?
- What side effects does it have?

### 2c. Identify the root cause

State the root cause explicitly:

```
Root cause: <exactly what is wrong, in which file, at which line>
Why: <why this causes the observed symptom>
```

**If you cannot identify the root cause, STOP.** Ask the user for more context. Do NOT guess.

---

## Step 3: Write a Regression Test

Before fixing, write a test that FAILS with the current code:

### 3a. Find existing test patterns

```bash
# Find tests for this area
# Search for existing test files
```

Read an existing test to learn:
- Test framework (vitest, jest, xunit, nunit)
- File naming convention
- Assertion style
- Setup/teardown patterns

### 3b. Write the test

Create a test that:
- Reproduces the bug's exact conditions
- Asserts the EXPECTED (correct) behavior
- Will FAIL on the current code and PASS after the fix

**Keep the test minimal.** One test case, one assertion. Do NOT write a test suite.

### 3c. Verify the test fails

```bash
<test-command>
```

If the test PASSES (bug not reproduced), your understanding of the root cause is wrong. Go back to Step 2.

---

## Step 4: Apply the Fix

### Fix the root cause, not the symptom

- Change the MINIMUM amount of code needed
- Do NOT refactor surrounding code
- Do NOT add defensive checks elsewhere "just in case"
- Do NOT change function signatures unless the signature IS the bug

### Common fix anti-patterns — DO NOT DO THESE

```
WRONG: Adding a try-catch to suppress the error
WRONG: Adding null checks everywhere instead of fixing why it's null
WRONG: Converting to a different pattern "while you're in there"
WRONG: Adding logging as the "fix" (logging helps debug, it's not a fix)
```

---

## Step 5: Verify

### 5a. Regression test now passes

```bash
<test-command>
```

### 5b. Existing tests still pass

```bash
<full-test-command>
```

### 5c. Build passes

```bash
<build-command>
```

---

## Step 6: Report

```
## Bug Fix

**Bug:** <symptom>
**Root cause:** <file:line — what was wrong>
**Fix:** <what was changed and why>

**Files changed:**
- <path> — <what changed>

**Test:** <test file:test name> — verifies the fix

**Verified:**
- Regression test passes: YES
- Existing tests pass: YES/NO
- Build passes: YES/NO
```

---

## Rules

1. **Diagnose before fixing.** Read the ENTIRE code path before changing anything. The bug is rarely where you first look.
2. **Test before fixing.** A fix without a regression test is a fix that will break again.
3. **Minimal fix.** Change the fewest lines possible. One-line fixes are better than redesigns.
4. **No drive-by refactors.** Fix the bug. That's it. Do NOT clean up, rename, or "improve" nearby code.
5. **If the test passes before your fix, your diagnosis is wrong.** Go back to Step 2.
6. **Stop after 3 fix attempts.** If the test still fails, you're probably fixing the wrong thing. STOP and report.
