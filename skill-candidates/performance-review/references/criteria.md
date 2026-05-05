# Performance Review — Criteria

---

## Dispositions

| Disposition | Meaning | PR Action |
|-------------|---------|-----------|
| **Blocking** | Must fix before merge. Risk of production failure, data loss, or correctness bug. | Request changes |
| **Non-blocking** | Should fix, does not stop the merge. Follow up in next sprint. | Comment with suggestion |
| **Discussion** | Tradeoff worth naming. Author may have good reasons. | Comment as FYI |
| **Praise** | Good optimization decision worth calling out. | Inline compliment |

---

## Disposition by Check

### Blocking

| Check | Why |
|-------|-----|
| Sync I/O in async function | Blocks the event loop — all concurrent operations stall. One call stalls everyone. |
| Database query in loop (N+1) | Query count grows linearly with data. Latency and DB load become unbounded. |
| Missing cleanup (event listener, interval) | Memory leak in long-running processes. Component unmount leaves ghost handlers. |

### Non-blocking

| Check | Why |
|-------|-----|
| No connection pool | Performance regression — expensive per-request, but not immediately catastrophic. |
| Missing timeout on external call | Risk of indefinite hang under partial failure — matters under load, not always in dev. |
| Full library import (lodash, moment) | Bundle size regression — low urgency unless at budget or on a critical path. |
| Cache without TTL | Data staleness or unbounded growth — severity depends on cache size and access pattern. |
| Unbounded collection | Memory leak risk — depends on how frequently the append path is exercised. |
| Sequential await in loop | Performance, not correctness — often worth a follow-up task rather than blocking merge. |
| SQL without LIMIT | Potential unbounded result set — severity depends on whether the table can grow. |

### Discussion

| Check | Why |
|-------|-----|
| Inline object/array props in JSX | Bypasses React.memo — worth naming if the component is in a hot render path. |
| Sequential API calls (no batching) | May be intentional (order matters, rate limits). Ask before suggesting gather. |
| Logging in hot path | Cosmetic unless profiler shows overhead. Mention, don't block. |
| No percentile tracking | Best practice — not a bug. Worth raising for new services, not for a small change. |

---

## Scope Rules

**Do not flag**:
- Issues in `*.test.*`, `*.spec.*`, `__tests__/` (except Blocking checks — flag those everywhere)
- Issues in `dist/`, `build/`, `.next/`, `*.generated.*`
- Issues in lines not present in the diff (pre-existing code)
- Patterns where context or a comment makes the choice intentional

**Flag everywhere (regardless of file type)**:
- Sync I/O in async functions
- N+1 database query patterns
- Missing cleanup on event listeners / intervals
