# Performance Review — Report Format

---

## Template

```
## Performance Review — [branch or description]
[N files reviewed · N findings: N blocking, N non-blocking, N discussion]

---

### 🚫 Blocking

#### `services/memory.py:47` — Sync I/O in async function
**Found**: `rows = psycopg2.connect(DSN).cursor().execute(query)`
**Risk**: Blocks the asyncio event loop — all concurrent requests stall until this returns.
**Fix**: `rows = await pg_pool.fetch(query)` (use existing pool)

---

### ⚠️ Non-blocking

#### `services/retrieval.py:83` — N+1 query pattern
**Found**: `for item in items: entity = await db.fetch("WHERE id=$1", item.id)`
**Impact**: One DB round trip per item — 100 items = 100 queries. Total latency scales linearly.
**Suggestion**: Batch with `await db.fetch("WHERE id = ANY($1)", item_ids)`

---

### 💬 Discussion

#### `api/search.ts:22` — Sequential embedding calls
**Found**: `for (const q of queries) { emb = await embed(q) }`
**Tradeoff**: Sequential — total latency = sum of all embed calls. Worth parallelizing if batch size grows. `Promise.all(queries.map(embed))` if order doesn't matter.

---

### ✅ Looks Good
- Connection pool with min/max sizing in `db/pool.py` — correct pattern
- Thundering herd protection with jitter in `cache/layer.py` — well done
[or: All N remaining checks passed.]
```

---

## Formatting Rules

**Found field**: exact line(s) from the diff. Max 3 lines; append `(N total — showing 3)` if more.

**Risk/Impact field**: state what actually happens in production, not what rule is violated. "Blocks the event loop" beats "synchronous call in async context."

**Fix/Suggestion field**: show corrected code, not a description of it. One-liner where possible.

**No commands in report**: show findings, not the grep that found them.

**No preamble**: start directly with the `## Performance Review` header.

**Collapse passed checks**: if all Tier 1 checks pass on more than 5 files, write `All N remaining checks passed.` — do not list each file.

**Praise sparingly**: note one or two genuinely good decisions. Omit if there are blocking findings.

**Empty diff or non-code only**: emit `No performance concerns — non-code changes only.` and stop.

---

## Comment Style

- **Blocking**: state the production failure mode. "All concurrent requests stall" beats "this is synchronous."
- **Non-blocking**: frame as impact at scale. "100 queries for 100 items" beats "N+1 anti-pattern."
- **Discussion**: acknowledge the author may have good reasons. "Worth it if batch sizes grow" beats "you should parallelize this."
- **Never**: "you should have", "this is wrong", "why did you". The code is the subject, not the author.
