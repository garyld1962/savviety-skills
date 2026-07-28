# Performance Advisor — Sharp Edges

---

## Optimizing the Wrong Thing

**Severity**: Critical
**Situation**: Optimizing code that "looks slow" without profiling.

```
THE MATH:
  Database query taking 450ms
  Loop you optimized: saves 0.1ms, runs 10×/request = 1ms saved
  Net impact: 0.2% improvement after 4 hours of work

WHERE TIME ACTUALLY GOES:
  Network: 100–500ms   Database: 10–100ms   Disk: 1–10ms   Loops: 0.001ms
```

**Fix**: Profile first. Target the 20% causing 80% of issues. Measure before and after.

---

## Async Is Not Parallel

**Severity**: Critical
**Situation**: Converting sync code to async expecting a speedup on CPU-bound work.

```python
# TRAP: This is NOT faster for CPU work — single thread, event loop blocked
async def process_all(items):
    return [await process_one(item) for item in items]  # sequential!

# For I/O-bound: asyncio.gather is correct
async def fetch_all(urls):
    return await asyncio.gather(*[fetch(url) for url in urls])

# For CPU-bound: ProcessPoolExecutor gives true parallelism
async def process_cpu(data):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(process_pool, heavy_fn, data)
```

**Rule**: asyncio = concurrency (one thread, cooperative). parallelism = multiple threads/processes.

---

## N+1 Queries

**Severity**: High
**Situation**: Each item in a loop triggers a separate database round trip.

```python
# TRAP: looks like simple attribute access, generates N queries
for memory in memories:
    entities = await db.fetch("WHERE memory_id=$1", memory.id)  # × N

# FIX: single query for all
entities_map = await batch_fetch_entities(memory_ids)
```

Detection: enable query logging. If query count scales with result count → N+1. Use `EXPLAIN ANALYZE` on suspicious queries.

---

## Cache Thundering Herd

**Severity**: High
**Situation**: Cache TTL expires. 100 concurrent requests all miss and hit the database simultaneously.

```
TTL expires at minute 5
→ 100 requests see cache miss at same time
→ 100 DB queries, not 1
→ DB overloads → timeouts → cascading failure
```

**Fix**: (1) Lock: only one caller fills the cache, others wait on the lock. (2) Stale-while-revalidate: serve stale while background refresh runs. (3) Jitter: `ttl * random(0.9, 1.1)` prevents synchronized expiry. See patterns.md.

---

## Connection Pool Exhaustion

**Severity**: High
**Situation**: Traffic spikes; requests timeout with "too many connections".

```
Pool size 10, concurrent requests 100
→ 90 requests queued waiting for connection
→ Timeouts cascade
→ "Pool too small" added as quick fix → DB overloaded instead
```

**Fix**: Size rule — `max_connections = cores × 2` (SSD) or `cores × 2 + spindles` (HDD). Set `command_timeout` so runaway queries don't hold connections forever. Monitor utilization — alert at 80%.

---

## React Memo Overuse

**Severity**: High
**Situation**: Wrapping every component in `React.memo`, `useMemo`, `useCallback` "just to be safe."

```tsx
// TRAP: memo adds overhead — comparison cost + memory
// Worthless when the component is cheap to render
const Badge = React.memo(({ label }) => <span>{label}</span>)

// TRAP: new object on every render bypasses memo anyway
<Chart config={{ threshold: 0.5 }} />  // new object ref each time
```

**Fix**: Profile with React DevTools Profiler first. Memo only expensive components with stable props. Wrap config objects with `useMemo` only when the wrapped component is actually expensive.

---

## Layout Thrashing

**Severity**: High
**Situation**: Reading layout properties inside a loop forces browser to synchronously recalculate layout on each read.

```ts
// TRAP: read → write → read → write forces reflow each iteration
items.forEach(item => {
    const h = item.offsetHeight           // forces reflow
    item.style.height = (h + 10) + 'px'  // write
})

// FIX: batch all reads, then all writes
const heights = items.map(item => item.offsetHeight)  // all reads
items.forEach((item, i) => { item.style.height = heights[i] + 10 + 'px' })
```

**Triggers**: `offsetHeight`, `offsetWidth`, `getBoundingClientRect`, `scrollTop`, `clientWidth` inside loops.

---

## p99 Invisible

**Severity**: Medium
**Situation**: Average latency looks healthy but 1% of users wait 10× longer.

```
avg: 50ms   p99: 5000ms
→ 1 in 100 users experiences "this app is broken"
→ Average dashboard shows everything is fine
```

**Fix**: Track p50/p90/p99 from day one. Set SLO targets against p99, not average. If p99 > 10× p50: investigate cold cache, lock contention, or GC pauses.

---

## Bundle Size Explosion

**Severity**: Medium
**Situation**: Full library import adds hundreds of KB to initial bundle.

```ts
// TRAP: imports entire lodash (~70KB gzipped)
import _ from 'lodash'
import moment from 'moment'  // ~67KB gzipped

// FIX: named imports or lighter alternatives
import debounce from 'lodash/debounce'
import { formatDate } from 'date-fns'  // tree-shakeable
```

**Detection**: `from 'lodash'` or `from 'moment'` in diff. Run `next analyze` or `webpack-bundle-analyzer` to find size regressions.
