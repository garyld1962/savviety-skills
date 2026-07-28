# Code Review: Optimization — Report Format

---

## Template

```
## Optimization Review — [branch or description]
[N files reviewed · N findings: N blocking, N non-blocking, N discussion]

---

### 🚫 Blocking

#### `path/to/file.ts:42` — Unbounded cache
**Found**: `const cache = new Map()`
**Risk**: Grows indefinitely — OOM crash after days/weeks in production.
**Fix**: `const cache = new LRUCache({ max: 500, ttl: 300_000 })`

---

### ⚠️ Non-blocking

#### `path/to/file.ts:87` — Sequential await in loop
**Found**: `for (const id of ids) { const item = await fetch(id) }`
**Impact**: Processes items one at a time — total time = sum of all durations.
**Suggestion**: `const items = await Promise.all(ids.map(id => fetch(id)))`

---

### 💬 Discussion

#### `path/to/service.ts:15` — Raw SQL bypassing repository layer
**Found**: `await db.raw('SELECT ...')`
**Tradeoff**: ~10× speedup, but couples UserService to the schema. Worth it? If yes, add a comment and a TODO for when the ORM supports this.

---

### ✅ Looks Good
- Parallel fetches in `api/users.ts` — good use of `Promise.all`
- LRU cache with TTL in `lib/session.ts` — correct pattern
[or: All N remaining checks passed.]
```

---

## Formatting Rules

**Found field**: show the exact line from the diff. Max 3 lines; append `(N total — showing 3)` if more.

**Fix field** (blocking and non-blocking): show the corrected code, not a description of it. One-liner where possible.

**No commands in the report**: show findings, not the grep commands that found them.

**No preamble**: start directly with the `## Optimization Review` header.

**Collapse passed checks**: if all Tier 1 checks pass on more than 5 files, write `All N remaining checks passed.` — do not list each file.

**Praise sparingly**: note one or two genuinely good decisions if present. Omit if there are blocking findings (save it for when they're addressed).

**Empty diff**: emit `No optimization concerns — non-code changes only.` and stop.

---

## Comment Style Guidelines

- **Blocking**: state the risk, not just the rule. "This will OOM" beats "use LRU cache."
- **Non-blocking**: frame as impact, not violation. "Processes sequentially" beats "anti-pattern detected."
- **Discussion**: acknowledge the author may have good reasons. "Worth discussing" beats "you should."
- **Never**: "you should have", "this is wrong", "why did you". The code is the subject, not the author.
