# TypeScript Review — Criteria

---

## Dispositions

| Disposition | Meaning | PR Action |
|-------------|---------|-----------|
| **Blocking** | Correctness risk — type escape hides a real bug or enables runtime failure | Request changes |
| **Non-blocking** | Should fix, does not stop merge. Type safety gap worth closing. | Comment with suggestion |
| **Discussion** | Tradeoff or design question. Author may have good reasons. | Comment as FYI |
| **Praise** | Genuinely good type-safety decision | Inline compliment |

---

## Disposition by Check

### Blocking

| Check | Why |
|-------|-----|
| `as any` / `: any` / `<any>` | Compiler trust override. Runtime errors become invisible to TypeScript. |
| `@ts-ignore` / `@ts-nocheck` | Suppresses real type errors. The underlying mismatch still exists at runtime. |
| Non-null assertion `!` without evidence | Crashes at runtime when the value is actually null or undefined. |
| Explicit `any` parameter | Interface mismatches on call sites become silent. Wrong argument types pass undetected. |

### Non-blocking

| Check | Why |
|-------|-----|
| `unknown` cast without narrowing | Bypasses the safety that `unknown` was meant to provide. Low risk, but closes a gap. |
| `Object` / `{}` as type | Too permissive — defeats structural typing. Worth a proper interface. |
| `Function` type | No parameter/return type info. A typed signature costs nothing and helps callers. |
| `@ts-expect-error` without description | Technical debt: future readers can't tell if the suppression is still needed. |
| Missing return type on exported function | Risk of accidental type widening when implementation changes. |

### Discussion

| Check | Why |
|-------|-----|
| `strictNullChecks: false` in tsconfig | Fundamental safety net disabled. Flag as architecture discussion, not immediate blocker. |
| Very wide union type (5+ members) | May be correct, but often signals a missing abstraction. Ask: is there a discriminated union here? |

---

## Scope Rules

**Do not flag**:
- Issues in `*.test.*`, `*.spec.*`, `__tests__/`, `*.generated.*`, `dist/`, `build/`, `.next/`
- Issues in lines not present in the diff (pre-existing code)
- `!` assertions in test files (common and accepted for test setup)
- `as any` in `*.generated.*` files (codegen output, not authored code)

**Always flag regardless of path**:
- `@ts-ignore` / `@ts-nocheck` — these are always a signal of a hidden problem
- Explicit `any` parameters on exported API boundaries
