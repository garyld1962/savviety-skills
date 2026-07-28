# TypeScript Review — Checks

All checks run against added lines only (see SKILL.md Step 2 for extraction command).

---

## Tier 1 — Auto-Flag (Correctness Risk)

Run against all changed `.ts`/`.tsx` files.

### `as any` / `<any>` Cast

```bash
grep -n "as any\b\|: any\b\|<any>" <file> | grep -v "//.*as any\|@ts-expect-error" | head -5
```

Flag every match. No context needed — this is always a type escape.

### `@ts-ignore` / `@ts-nocheck`

```bash
grep -n "@ts-ignore\|@ts-nocheck" <file> | head -5
```

Flag every match. `@ts-expect-error` without a description is also flagged (see below).

### `@ts-expect-error` Without Description

```bash
grep -n "@ts-expect-error" <file> | grep -v "@ts-expect-error\s\+\S" | head -5
```

Flag if the directive has no explanation text following it on the same line.

### Explicit `any` Parameter Type

```bash
grep -nE "function\s+\w+\s*\([^)]*:\s*any\b|=\s*\([^)]*:\s*any\b" <file> | head -5
```

Flag parameters typed as `any` on added function signatures. Hides interface mismatches.

### Non-Null Assertion on Potentially-Null Values

```bash
grep -nE "\b\w+!\.\w+|\b\w+!\[|\)!\." <file> | grep -v "//.*safe\|//.*guaranteed\|//.*cannot be null" | head -5
```

Flag `!` usage with no explanatory comment. Requires context check: read ±5 lines to determine if the value is demonstrably non-null (e.g., immediately after a null check). If demonstrably safe, skip.

---

## Tier 2 — Judgment Required

Apply to `src/`, `lib/`, `app/` paths. Read context before flagging.

### `unknown` Cast Directly to Specific Type (No Narrowing)

```bash
grep -nE "\bunknown\b.{0,40}as\s+[A-Z]\w+|\bas\s+[A-Z]\w+.{0,40}\bunknown\b" <file> | head -5
```

Flag if `unknown` is cast to a concrete type without a preceding type guard. Skip if a type guard function call or `instanceof`/`typeof` check is visible within ±5 lines.

### `Object` / `{}` as Type

```bash
grep -nE ":\s*Object\b|:\s*\{\s*\}" <file> | grep -v "Record<\|extends\s*{}" | head -5
```

Flag bare `Object` or empty `{}` type annotations. These accept nearly anything and lose all type information.

### `Function` Type

```bash
grep -nE ":\s*Function\b" <file> | head -5
```

Flag `Function` type — no parameter or return type information. Always replaceable with a typed signature.

### Missing Return Type on Exported Function

```bash
grep -nE "^export\s+(async\s+)?function\s+\w+\s*\([^)]*\)\s*\{|^export\s+const\s+\w+\s*=\s*(async\s+)?\([^)]*\)\s*=>" <file> | grep -v ":\s*\S" | head -5
```

Flag exported functions with no explicit return type annotation. Inference can widen unexpectedly when the implementation changes.

---

## Tier 3 — Discussion

Only apply if `tsconfig.json` or `tsconfig.*.json` is in the diff, or if the PR is a significant structural change.

### `strictNullChecks` Disabled

```bash
grep -n '"strictNullChecks"\s*:\s*false\|"strict"\s*:\s*false' tsconfig*.json 2>/dev/null | head -5
```

Flag any explicit disabling of strict flags in a tsconfig file in the diff.

### Very Wide Union Type (5+ Members)

```bash
grep -nE "type\s+\w+\s*=\s*(\w+\s*\|){4,}" <file> | head -5
```

Flag union types with 5 or more members as a discussion point — may indicate a missing abstraction (discriminated union, enum, or interface hierarchy).
