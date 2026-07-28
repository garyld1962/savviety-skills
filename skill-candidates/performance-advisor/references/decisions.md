# Performance Advisor — Decisions

---

## When to Optimize

Only optimize when you can answer yes to all three:
1. **Measured** — profiler or CWV data confirms this is a bottleneck
2. **Impactful** — fixing it meaningfully changes user experience
3. **Safe** — characterization tests exist before touching the code

**ROI heuristic**: (% of total time) × (achievable speedup) × (user impact) — rank candidates, pick the top one.

| Where time actually goes | Typical range |
|--|--|
| Network requests | 100–500ms |
| Database queries | 10–100ms |
| Disk I/O | 1–10ms |
| CPU / loop micro-opts | 0.001ms |

Profile before assuming. The slow thing is almost always a network or DB call.

---

## Sync vs Async vs Parallel

| Work type | Solution | Why |
|--|--|--|
| I/O-bound (network, DB, disk) | `asyncio` / `async/await` | Concurrency during wait |
| CPU-bound (parsing, ML inference, compression) | `ProcessPoolExecutor` | True parallelism across cores |
| Blocking sync library (legacy, no async API) | `ThreadPoolExecutor` | Offload without blocking event loop |
| JS event loop blocking | `setTimeout(fn, 0)` or Web Worker | Yield to browser |

**The trap**: Converting sync code to async expecting a speedup for CPU-bound work. asyncio runs on one thread. CPU work blocks the event loop.

---

## Cache Design

Four questions before adding a cache:

1. **How stale can it be?** → sets TTL
2. **How large can it grow?** → sets max size (no max = eventual OOM)
3. **What happens on cache expiry under load?** → design for thundering herd (see patterns.md)
4. **How do you invalidate it?** → have a plan before shipping

**Cache hierarchy**:
- L1 (process memory): TTL 30–60s, max ~1000 entries, not shared
- L2 (Redis): TTL minutes–hours, shared across instances
- CDN: TTL hours–days, public content only

**Cache-aside vs write-through**: cache-aside is simpler and more resilient; write-through keeps data fresher but doubles write latency.

---

## Where to Look First: Frontend vs Backend

```
User reports slowness
├── First: measure — browser DevTools, Lighthouse, PerformanceObserver
│
├── CWV issue (LCP > 2.5s, INP > 200ms, CLS > 0.1)
│   ├── LCP → image size, server response time, render-blocking resources
│   ├── INP → main thread blocking, long tasks, React reconciliation
│   └── CLS → layout shifts, missing image dimensions, late-injected content
│
├── API/backend latency
│   ├── Check query count (N+1?), query execution plans (EXPLAIN ANALYZE)
│   ├── Check p99 — if much higher than p50, look for cold cache or lock contention
│   └── Check connection pool utilization
│
└── Bundle size
    ├── Run webpack-bundle-analyzer or next analyze
    ├── Find large imports (lodash, moment, full icon sets)
    └── Check for missing code splitting on large routes
```

---

## p99 vs Average

Always instrument at p50, p90, p95, p99. Report p99 to stakeholders.

```
Average 50ms + p99 5000ms = "users complain but dashboards look fine"
```

**Rule**: if p99 > 10× p50, investigate tail latency specifically — likely a cold cache, lock contention, or GC pause.

**SLO template**: define targets before shipping, not after complaints.
| Operation | p50 target | p99 target |
|--|--|--|
| Page load | 500ms | 3000ms |
| API read | 50ms | 500ms |
| API write | 100ms | 1000ms |
