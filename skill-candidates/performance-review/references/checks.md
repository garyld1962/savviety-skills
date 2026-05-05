# Performance Review — Checks

All checks run against added lines only (see SKILL.md Step 2 for extraction command).
Language tags: `[py]` = Python only, `[ts]` = TypeScript/JavaScript only, no tag = both.

---

## Tier 1 — Auto-Flag (High Confidence)

### Sync I/O in Async Function `[py]`

```bash
grep -n "async def" <file> | head -5
grep -n "requests\.get\|time\.sleep\|open(.*\.read\|psycopg2\." <file> | head -5
```

Flag if a sync I/O call appears in a file that uses `async def`. Blocks the event loop — all concurrent operations stall.

### Database Query in Loop `[py]`

```bash
grep -nE "for .+ in .+:|await .+db\.|await .+fetch\b|await .+execute\b" <file> | head -10
```

Flag if an `await db.*` / `await fetch` / `await execute` appears on a line following a `for` loop. Classic N+1 — query count scales with result count.

### No Connection Pool `[py]`

```bash
grep -n "asyncpg\.connect(\|psycopg2\.connect(\|redis\.Redis([^)]*)" <file> \
  | grep -v "connection_pool\|create_pool" | head -5
```

Flag any per-request connection creation. Amortize connection cost with a pool.

### Missing Timeout on External Call `[py]`

```bash
grep -n "aiohttp\|httpx\|requests\.get\|requests\.post" <file> \
  | grep -v "timeout" | head -5
```

Flag HTTP calls without a timeout parameter. May hang indefinitely.

### Full Library Import `[ts]`

```bash
grep -n "from 'lodash'\|from \"lodash\"\|require('lodash')\|from 'moment'\|from \"moment\"" <file> | head -5
```

Always flag. Named imports (`from 'lodash/debounce'`) are fine.

### Missing Cleanup (Event Listener / useEffect) `[ts]`

```bash
grep -n "addEventListener(\|setInterval(\|setTimeout(" <file> | head -5
```

Flag if no corresponding `removeEventListener` / `clearInterval` / `clearTimeout` exists in the same diff. Check `useEffect` for missing cleanup return.

### Inline Object/Array Props in JSX `[ts]`

```bash
grep -n "=\s*{[^}]*}\|=\s*\[" <file> | grep -v "className\|style" | head -5
```

Flag non-trivial object or array literals as JSX props — creates a new reference on every render, bypassing `React.memo`. Check if the parent re-renders frequently.

---

## Tier 2 — Judgment Required

Apply to `src/`, `lib/`, `app/` files only. Check context before flagging.

### Cache Without TTL

```bash
grep -n "cache\.set(\|redis\.set(" <file> \
  | grep -v "ttl\|ex=\|px=\|expire" | head -5
```

Flag if a cache write has no expiry. Data becomes stale indefinitely, or grows without bound. Skip if the caching library enforces global TTL via config.

### Unbounded Collection

```bash
grep -n "\.append(\|\.push(" <file> | head -10
```

Flag if the append/push is inside a loop with no size guard (`if len(...) < MAX`) and no subsequent slice/drain. Potential memory leak in long-running processes.

### Sequential Await in Loop

```bash
grep -n "await " <file> | head -15
```

Flag only if `await` appears inside a `for`, `for...of`, or `while` loop. Skip if a comment like `// sequential required` or `// order matters` is within 3 lines. Performance issue, not a correctness issue — non-blocking.

### SQL Without LIMIT

```bash
grep -n "SELECT.*FROM" <file> | grep -iEv "LIMIT|TOP|FETCH NEXT" | head -5
```

Flag queries on tables that could grow unbounded. Skip if the table is known to be small (config, roles, etc.) — use context.

---

## Tier 3 — Discussion Only

### Sequential API Calls (No Batching)

```bash
grep -nE "for .* in .*:|await .*(embed|llm|api)\(" <file> | head -10
```

Flag sequential calls to embedding APIs or external services inside loops. `asyncio.gather()` / `Promise.all()` may be applicable.

### Logging in Hot Path

```bash
grep -nE "(for|while).+logger\.(debug|info)|logger.*json\.dumps" <file> | head -5
```

Note if structured logging or JSON serialization occurs inside a tight loop. Low severity unless profiler confirms overhead.

### No Percentile Tracking in New Service Code

```bash
grep -n "latency\|response_time\|duration" <file> | grep -v "p99\|p95\|percentile\|histogram" | head -5
```

Flag new service-layer code that tracks latency as average/sum only. Suggest adding a Prometheus Histogram or equivalent. Discussion, not blocking.
