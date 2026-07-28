# Code Quality — Checks

All checks run against added lines only. Extract with:
```bash
git diff <base_ref> -- <file> | grep '^+' | grep -v '^+++' | head -200
```

---

## Tier 1 — Flag (High Confidence, Non-blocking)

### Single-Letter Variable Names

```bash
grep -nE "^\+\s*(const|let|var)\s+[a-hj-z]\s*=" <file> \
  | grep -v "for\s*(" | head -5
```

`i`, `j`, `k` are exempt (loop counters). Single-param arrow functions (`.map(x =>`) are exempt. Flag everything else.

### Boolean Missing is/has/can/should Prefix

```bash
grep -nE "^\+\s*(const|let)\s+(?!(is|has|can|should|will|did))[a-z]\w*\s*=\s*(true|false)" <file> | head -5
```

Flag `const active = true` — should be `isActive`. Flag `let loading = false` — should be `isLoading`.

### Magic Numbers

```bash
grep -nE "^\+.*(===|!==|[<>]=?)\s*[0-9]{2,}|setTimeout\([^,]+,\s*[0-9]{4,}\)" <file> \
  | grep -v "test\|spec\|config\|\.json" | head -5
```

Skip test files and config files. Skip obvious values: `/ 100`, `[0]`, `[1]`. Flag anything requiring a comment to understand.

### Functions Exceeding 40 Lines [js/ts]

```bash
grep -n "^\+\s*function\s\+\w\+\|^\+\s*const\s\+\w\+\s*=\s*\(async\s*\)\?(" <file> | head -10
```

Count lines between opening and closing brace. Flag if >40. Note: use judgment — pure transformations and sequential pipelines may be fine. Flag only when distinct responsibilities are visible.

### Nesting Depth >3

```bash
grep -nP "^\+(\s{12,}|\t{3,})" <file> | head -5
```

12 spaces or 3 tabs indicates 3+ levels of indentation. Flag and note guard clause pattern as the fix.

### Functions with >4 Parameters

```bash
grep -nE "^\+\s*(function\s+\w+|const\s+\w+\s*=\s*(async\s*)?\()\s*\([^)]{40,}\)" <file> | head -5
```

Suggest options object when flagged.

---

## Tier 2 — Judgment Required

Apply to `src/`, `lib/`, `app/` files. Skip if context justifies it.

### Commented-Out Code Blocks

```bash
grep -nE "^\+\s*//\s*(const|let|var|function|if|for|while|return|class)\s" <file> | head -5
```

Flag if 2+ consecutive commented-out lines. Skip if comment explains a temporary workaround with a ticket reference.

### TODO/FIXME Without Issue Reference

```bash
grep -nE "^\+\s*//\s*(TODO|FIXME|HACK|XXX)" <file> \
  | grep -vE "#[0-9]+|https?://" | head -5
```

Flag TODOs with no issue reference. `// TODO: fix this` is a flag. `// TODO: #1234` is fine.

### Negated Boolean Names

```bash
grep -nE "^\+\s*(const|let)\s+(isNot|hasNo|isNever|cantNot|notIs)\w+\s*=" <file> | head -5
```

Also catch: `isNotValid`, `hasNoErrors`, `isNotReady`. These should be inverted: `isValid = false` instead of `isNotValid = true`.

### `else` After `return`

```bash
grep -nE "^\+\s*\}\s*else\s*\{" <file> | head -5
```

Flag only when the preceding block clearly ends with `return`. Skip symmetric cases where both branches are same length. Prefer early return.

---

## Tier 3 — Discussion Only

### Deep Inheritance (>2 levels) [js/ts]

```bash
grep -nE "^\+\s*class\s+\w+\s+extends\s+" <file> | head -5
```

Not a flag — note as discussion if inheritance chain is visible. Prefer composition.

### Public Methods With No Usages

```bash
grep -nE "^\+\s*(public\s+)?\w+\s*\([^)]*\)\s*\{" <file> | head -5
```

Cross-reference with codebase search. Discussion if no usages found — may be dead code or a public API.

### Copy-Paste Duplication (3+ Nearly-Identical Blocks)

Visually inspect the diff for repeated blocks of 5+ lines with only variable names changed. Flag as Rule-of-Three discussion: is there a pattern ready to abstract?
