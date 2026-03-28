# Test Quality Specialist

**Domain:** `test-quality`

Reviews test files for quality and identifies missing test coverage. Universal to any TypeScript project using vitest, jest, or similar.

## Scope

- `**/*.test.ts` and `**/*.test.tsx` (test file quality)
- Source files WITHOUT corresponding test files (coverage gaps)

## Context Required Before Review

- **`.github/copilot-instructions.md`** — testing conventions, test runner, coverage expectations
- **Workspace config** — which packages should have tests

## Review Checklist

### Rule 1: Missing Test Files for Core Logic (Medium, 0.85)

**What:** Source files containing core business logic should have companion test files.

**Special case:** If no tests exist in the entire project, emit a single Info finding, NOT per-file findings.

---

### Rule 2: Tests Asserting Implementation Not Behavior (Medium, 0.75)

**What:** Tests should verify observable behavior, not internal implementation details.

**Exception:** Mock assertions are appropriate for verifying messages published, emails sent, external API calls.

---

### Rule 3: Missing Error Path Tests (Medium, 0.70)

**What:** Tests should cover: successful execution, invalid input, dependency failure, edge cases.

---

### Rule 4: Test Isolation Issues (High, 0.80)

**What:** Tests should be independent. Shared mutable state without cleanup causes unpredictable failures.

---

### Rule 5: Missing async/await in Assertions (High, 0.85)

**What:** Assertions on async operations must properly await.

---

### Rule 6: Meaningful Test Descriptions (Low, 0.80)

**Violation:** `it('works', ...)`, `it('test 1', ...)`

---

### Rule 7: Hardcoded External Dependencies in Unit Tests (Medium, 0.70)

**What:** Unit tests should not depend on live external services.

**Exception:** Integration tests (`*.integration.test.ts`) legitimately use real services.

## Output

Domain is always `"test-quality"`. Emit findings conforming to the schema in the main code-review prompt.
