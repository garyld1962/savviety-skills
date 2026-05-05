# TypeScript Review — Report Format

---

## Template

```
## TypeScript Review — [branch or description]
[N files reviewed · N findings: N blocking, N non-blocking, N discussion]

---

### Blocking

#### `src/api/users.ts:34` — `as any` cast
**Found**: `const user = response.data as any`
**Risk**: Compiler no longer checks downstream usage of `user`. Type errors become runtime crashes.
**Fix**: `const user = UserSchema.parse(response.data)` or add a type guard function.

---

### Non-blocking

#### `src/lib/parser.ts:89` — `Function` type
**Found**: `onComplete: Function`
**Impact**: No parameter or return type info for callers.
**Suggestion**: `onComplete: (result: ParseResult) => void`

---

### Discussion

#### `tsconfig.json:8` — `strictNullChecks` disabled
**Found**: `"strictNullChecks": false`
**Note**: Disabling this flag is the single largest source of undefined-is-not-an-object crashes. Consider enabling with a phased fix plan.

---

### Looks Good
- Type guard in `src/lib/auth.ts` — proper `isUser()` predicate, no assertion needed
[or: All N remaining checks passed.]
```

---

## Formatting Rules

**Found field**: exact line from the diff. Max 3 lines; append `(N total — showing 3)` if more.

**Risk/Fix field** (blocking): state the runtime consequence, then the concrete fix. One-liner fix where possible.

**Impact/Suggestion field** (non-blocking): frame as cost, not violation. Show the typed alternative.

**No commands in the report**: show findings, not the grep that found them.

**No preamble**: start directly with `## TypeScript Review` header.

**Collapse passed checks**: if more than 8 checks passed with no findings, emit `All N remaining checks passed.`

**Praise sparingly**: one or two genuinely good type-safety decisions if present. Skip if blocking findings exist.

**Empty diff**: emit `No TypeScript concerns — no .ts/.tsx changes.` and stop.

---

## Comment Style

- **Blocking**: name the runtime consequence. "Compiler no longer validates" beats "avoid any."
- **Non-blocking**: name the gap. "No parameter type info for callers" beats "use typed function."
- **Discussion**: acknowledge the author may have context. "Consider enabling" beats "you must enable."
- Never: "you should have", "this is wrong", "why did you". The code is the subject, not the author.
