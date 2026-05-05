# Test Strategist — Checks

All checks run against test files only (`*.test.*`, `*.spec.*`, `__tests__/`).
Extract added lines: `git diff <base_ref> -- <file> | grep '^+' | grep -v '^+++' | head -200`

---

## Tier 1 — Blocking (False Confidence)

### Test With No Meaningful Assertion

```bash
grep -n "^\+\s*it\s*(\|^\+\s*test\s*(" <file> | head -10
```

For each matched test block, check that an `expect(` call with a specific matcher appears inside it. Flag if:
- No `expect(` at all in the block
- Only `toBeTruthy()`, `toBeDefined()`, `not.toBeNull()`, `not.toBeUndefined()` assertions

```bash
grep -nE "^\+.*expect\(.*\)\.(toBeTruthy|toBeDefined|not\.toBeNull|not\.toBeUndefined)\(" <file> | head -5
```

### Empty Test Body

```bash
grep -nE "^\+\s*(it|test)\(['\"][^'\"]+['\"],\s*(async\s*)?\(\s*\)\s*=>\s*\{\s*\}\s*\)" <file> | head -5
```

### Skipped Test Without Explanation

```bash
grep -nE "^\+.*(\.skip\(|xit\(|xdescribe\(|it\.skip\(|test\.skip\()" <file> \
  | grep -vE "TODO|FIXME|BUG|https?://#" | head -5
```

Flag skipped tests with no comment explaining why. A skip with a ticket reference is fine.

### Sleep/setTimeout in Test

```bash
grep -nE "^\+.*(await\s+new\s+Promise.*setTimeout|await\s+sleep\(|await\s+delay\(|setTimeout\([^,]+,\s*[0-9]{3,}\))" <file> | head -5
```

Always flag. Fixed delays are timing dependencies — flaky by construction.

---

## Tier 2 — Judgment Required

### Assertion on Implementation Detail

```bash
grep -nE "^\+.*toHaveBeenCalledWith\([^)]*SELECT|^\+.*toHaveBeenCalledWith\([^)]*INSERT|^\+.*\.mock\.calls|^\+.*\.innerHTML" <file> | head -5
```

Flag if asserting on SQL string content or internal call signatures. Suggest testing observable output instead.

### Test With Only Happy Path

```bash
grep -n "^\+\s*describe\|^\+\s*it\|^\+\s*test" <file> \
  | grep -vE "error|fail|invalid|empty|null|undefined|reject|throw|negative|missing" | head -10
```

If a test file has 5+ test cases and none mention error/failure/edge conditions, flag as likely happy-path only. Apply judgment — some utility functions have no error paths.

### Excessive Mocking (4+ jest.mock/vi.mock calls)

```bash
grep -cE "^\+.*(jest\.mock|vi\.mock)\(" <file>
```

Flag if count >= 4. Suggest considering an integration test with real dependencies.

---

## Tier 3 — Discussion

### Very Long Test Name (>80 chars)

```bash
grep -nE "^\+\s*(it|test)\(['\"].{80,}['\"]" <file> | head -5
```

Sometimes a smell of testing too many things at once. Discuss whether the test should be split.

### Test File With No Edge Cases

Flag if a test file covers a function with explicit error handling (visible in the source file) but has no test cases for error paths. Discussion: the error handling is untested.
