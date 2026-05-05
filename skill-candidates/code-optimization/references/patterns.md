# Code Optimization — Patterns

---

## Optimization Loop

**When**: Any performance work, before any other pattern.

```
1. MEASURE   — profile the actual system, not your intuition
2. IDENTIFY  — find the real bottleneck (usually not what you expect)
3. VALIDATE  — is it worth the complexity cost?
4. OPTIMIZE  — make one targeted change
5. VERIFY    — measure the improvement
6. MONITOR   — alert on regression

Never skip step 1. Never combine steps 4 and 5.
```

**Priority formula**: `Impact = Users affected × Severity × Frequency`. Optimize highest-impact first.

---

## Strangler Fig

**When**: Migrating a legacy system without a big-bang rewrite.

```
Step 1: Insert proxy layer — all traffic still hits old system
Step 2: Route one endpoint to new implementation
Step 3: Monitor, fix, increase coverage
Step 4: Old system shrinks as new system grows
Step 5: Delete old system when proxy routes nothing to it

Rollback = routing change. Zero downtime at every stage.
No new features on old system. Max 3 months — or you have two legacy systems.
```

---

## Incremental Refactoring

**When**: Improving code quality without stopping feature work.

```
1. IDENTIFY  — "this is hard to change" or "this pattern is in 5 places"
2. SCOPE     — smallest change that helps; fits in one PR
3. TEST      — characterization tests if behavior is unclear
4. REFACTOR  — small steps, run tests after each
5. VERIFY    — deploy, monitor

Key techniques:
- Extract function (logic > 10 lines, or 3+ callers)
- Rename for clarity (d → userData)
- Extract variable (complex conditions → named boolean)
- Inline unnecessary abstraction
```

**Budget**: 20% of sprint capacity, continuously. Never a "refactoring sprint" — scope creep kills them.

---

## Dead Code Elimination

**When**: Reducing complexity and bundle size.

```
FIND:
npx knip           # Files and exports never imported
npx depcheck       # npm packages never required
npx ts-prune       # TypeScript exports never used
git log -S "name"  # When was this last touched?

VERIFY before deleting:
- Dynamic imports (string-based require, eval)
- Reflection usage
- Config file references
- External callers (APIs, scripts)

PROCESS:
1. Add deprecation warning, monitor for 2 weeks
2. No warnings? Safe to delete.
3. Delete, run full test suite, deploy
```

---

## Parallel Operations

**When**: Multiple independent I/O operations in sequence.

```javascript
// Sequential: total = sum of all durations (300ms)
const user   = await getUser(id)    // 100ms
const orders = await getOrders(id)  // 150ms
const prefs  = await getPrefs(id)   // 50ms

// Parallel: total = slowest one (150ms)
const [user, orders, prefs] = await Promise.all([
  getUser(id), getOrders(id), getPrefs(id)
])

// With concurrency limit (avoid overwhelming downstream)
import pMap from 'p-map'
const results = await pMap(ids, fetchItem, { concurrency: 10 })
```

**Only parallelize when**: operations are independent, I/O-bound, and the resource can handle concurrent load. Never for dependent operations or CPU-bound work.

---

## Caching Strategy

**When**: The same expensive result is needed repeatedly.

```
Cache levels (cheapest → most complex):
  Browser cache   → static assets, long TTL, versioned filenames
  CDN             → public API responses, shared content
  App memory      → LRU cache with max entries + TTL
  Database        → materialized views, query cache

Cache-aside pattern (most common):
  function get(key) {
    const cached = cache.get(key)
    if (cached) return cached
    const result = expensiveSource(key)
    cache.set(key, result, { ttl: 300_000 })
    return result
  }

Mandatory constraints:
  - Set maximum size (LRUCache: { max: 1000 })
  - Set TTL (never cache forever)
  - Monitor hit rate (target > 90%)
  - Plan invalidation before implementing
```

**Rule**: No cache without a named invalidation strategy. "We'll figure it out" is how you get stale data for 6 months.
