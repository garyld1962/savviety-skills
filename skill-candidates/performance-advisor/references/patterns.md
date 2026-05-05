# Performance Advisor — Patterns

---

## Measure First

Profile before touching anything. Intuition is wrong.

```python
# Python — cProfile baseline
import cProfile, pstats, io, time

with cProfile.Profile() as prof:
    result = expensive_function()

s = io.StringIO()
pstats.Stats(prof, stream=s).sort_stats('cumulative').print_stats(20)
print(s.getvalue())  # Top 20 hotspots
```

```ts
// Browser — Core Web Vitals baseline
import { onLCP, onINP, onCLS, onTTFB } from 'web-vitals'

onLCP(m => console.log('LCP', m.value))   // Target < 2.5s
onINP(m => console.log('INP', m.value))   // Target < 200ms
onCLS(m => console.log('CLS', m.value))   // Target < 0.1
onTTFB(m => console.log('TTFB', m.value)) // Target < 800ms
```

**Rule**: Optimize only the top entry in the profile. Re-measure after each change.

---

## Async vs Parallel Dispatch

`asyncio` is concurrent, not parallel. CPU-bound work blocks the event loop.

```python
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import asyncio

executor_cpu = ProcessPoolExecutor(max_workers=4)   # CPU-bound
executor_io  = ThreadPoolExecutor(max_workers=10)   # Blocking I/O

async def cpu_task(data: bytes):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor_cpu, parse_heavy, data)

async def blocking_lib_call(params):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor_io, legacy_sync_lib, params)

# I/O-bound: asyncio.gather is correct
async def fetch_all(urls: list[str]):
    return await asyncio.gather(*[fetch(url) for url in urls])
```

**Decision**: I/O-bound → asyncio. CPU-bound → ProcessPoolExecutor. Blocking library → ThreadPoolExecutor.

---

## Multi-Level Caching with Thundering Herd Protection

```python
import asyncio, random, time

class Cache:
    def __init__(self):
        self._store = {}
        self._locks: dict[str, asyncio.Lock] = {}

    async def get_or_compute(self, key: str, fn, ttl=300, stale_ttl=60):
        entry = self._store.get(key)
        now = time.time()

        if entry and now < entry['soft_exp']:      # Fresh hit
            return entry['value']
        if entry and now < entry['hard_exp']:      # Stale — refresh in background
            asyncio.create_task(self._refresh(key, fn, ttl, stale_ttl))
            return entry['value']

        # Miss — acquire lock so only one caller fills
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        async with self._locks[key]:
            if (entry := self._store.get(key)) and now < entry['soft_exp']:
                return entry['value']               # Another caller filled it
            value = await fn()
            jitter = random.uniform(0.9, 1.1)       # Prevent synchronized expiry
            self._store[key] = {
                'value': value,
                'soft_exp': now + ttl * jitter,
                'hard_exp': now + (ttl + stale_ttl) * jitter,
            }
            return value
```

**Rule**: Every cache needs: a max size, a TTL, and thundering herd protection on cold start.

---

## Batch Loading (N+1 Prevention)

```python
# Bad: N+1 — one query per item
async def load_items_bad(ids):
    return [await db.fetchrow("SELECT * FROM items WHERE id=$1", id) for id in ids]

# Good: one query for all
async def load_items(ids: list[UUID]) -> dict[UUID, Item]:
    rows = await db.fetch("SELECT * FROM items WHERE id = ANY($1)", ids)
    return {row['id']: Item.from_row(row) for row in rows}

# With relations — parallel queries instead of serial
async def load_with_relations(ids):
    memories, entities, relations = await asyncio.gather(
        db.fetch("SELECT * FROM memories WHERE id = ANY($1)", ids),
        db.fetch("SELECT * FROM entities WHERE memory_id = ANY($1)", ids),
        db.fetch("SELECT * FROM relations WHERE source_id = ANY($1)", ids),
    )
    return _assemble(memories, entities, relations)
```

**Detection**: Enable query logging during development. If query count scales with result count, you have N+1.

---

## Connection Pooling

```python
import asyncpg
from redis.asyncio import ConnectionPool, Redis

# PostgreSQL — size for your DB: (cores * 2) for SSD, (cores * 2 + spindles) for HDD
pg_pool = await asyncpg.create_pool(
    dsn=DATABASE_URL,
    min_size=5, max_size=20,
    max_inactive_connection_lifetime=300,
    command_timeout=30,
)

# Redis
redis = Redis(connection_pool=ConnectionPool.from_url(
    REDIS_URL, max_connections=50, socket_timeout=5,
))
```

**Rule**: One pool per external service, initialized at startup, closed at shutdown. Never `asyncpg.connect()` per request.

---

## Frontend: Bundle + React Optimization

```ts
// Lazy-load heavy routes — removes them from initial bundle
const Dashboard = React.lazy(() => import('./Dashboard'))

// next.config.js — tree-shake large libraries
experimental: { optimizePackageImports: ['lodash-es', 'date-fns'] }

// Memoize only when re-render is measurably expensive
// Bad: memo on everything — adds overhead, hides real problems
const Item = React.memo(({ id, name }) => <div>{name}</div>)  // not worth it

// Good: memo when parent re-renders frequently AND child is expensive
const HeavyChart = React.memo(Chart, (prev, next) => prev.data === next.data)

// Stable references prevent memo from being bypassed
const handler = useCallback(() => onSelect(id), [id, onSelect])
const config = useMemo(() => ({ threshold: 0.5 }), [])  // only if truly stable
```

**Layout thrashing**: Never read layout properties (`offsetHeight`, `getBoundingClientRect`) inside a loop. Batch reads before writes.
