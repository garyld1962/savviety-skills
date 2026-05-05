# Code Optimization — Sharp Edges

---

## Premature Optimization

**Severity**: Critical
**Situation**: Optimizing code that "looks slow" before profiling.

```
THE TRAP:
"This loop looks inefficient."
→ 4 hours spent, 200 lines of complex code added
→ Measurement shows: loop runs 10x/request, saves 0.1ms
→ Real bottleneck was a database query taking 450ms

WHERE TIME ACTUALLY GOES:
  Network requests:    100–500ms
  Database queries:    10–100ms
  Disk I/O:            1–10ms
  Loop micro-opts:     0.001ms
```

**Fix**: Profile first. Target the 20% causing 80% of issues. Measure before and after every change.

---

## Big Bang Rewrite

**Severity**: Critical
**Situation**: Rewriting a large system all at once.

```
70% fail or are abandoned. Average: 3× longer than estimated.
Often reintroduce old bugs. Team morale destroyed by month 4.
```

**Fix**: Strangler Fig. One module at a time. Ship each piece to production before starting the next. Old system must keep working throughout.

**Exception**: System is < 1 month to rewrite, has clear boundaries, and team fully understands the domain.

---

## Optimization Without Tests

**Severity**: Critical
**Situation**: Refactoring or optimizing code with no test coverage.

```
WHAT GOES WRONG:
  Edge case broken → customer data corrupted
  "It worked in my testing" (happy path only)
  No way to know what you changed

CHARACTERIZATION TEST (write before touching code):
  test('calculatePrice current behavior', () => {
    expect(calculatePrice(100, 'premium')).toBe(85)
    expect(calculatePrice(100, 'basic')).toBe(100)
    expect(calculatePrice(0, 'premium')).toBe(0)
    expect(calculatePrice(-1, 'basic')).toBe(0)  // edge case!
  })
  // Now you know exactly what to preserve
```

**Rule**: No tests → no refactor. "I don't have time for tests" means "I don't have time to refactor."

---

## Hidden Side Effects

**Severity**: Critical
**Situation**: Optimization silently changes observable behavior.

```
CLASSIC TRAP (sync → async):
  // Before: sequential, logging, notifications in order
  items.forEach(item => { process(item); log(item); notify() })

  // "Optimized": parallel — logging gone, notification order broken
  await Promise.all(items.map(item => process(item)))

SIDE EFFECTS THAT DISAPPEAR:
  Logging/monitoring, analytics, event emission order, external API calls
```

**Fix**: Before optimizing, list all side effects explicitly. After optimizing, verify each one still occurs with the same behavior. Test for side effects, not just outputs.

---

## Memory Leak Introduction

**Severity**: Critical
**Situation**: Caching or memoization without bounds causes memory to grow indefinitely.

```
THE TRAP:
  const cache = new Map()          // No max size
  function getData(id) {
    if (!cache.has(id)) cache.set(id, query(id))
    return cache.get(id)
  }
  // Works perfectly for 2 weeks, then OOM crash

OTHER SOURCES:
  Event listeners added without cleanup
    window.addEventListener('resize', handler)  // never removed
  
  Intervals not cleared
    setInterval(poll, 1000)  // component unmounts, interval runs forever
  
  Closures holding references to large objects
```

**Fix**: Every cache needs `max` entries AND a TTL. Every `addEventListener` needs a matching `removeEventListener`. Every interval needs a `clearInterval`. Profile memory over time, not just at startup.

---

## Performance Cliff

**Severity**: High
**Situation**: Optimization works in testing, fails catastrophically at production scale.

```
EXAMPLES:
  O(n²) algorithm: fine at n=100, crashes at n=10,000
  Cache miss: 1ms hit → 500ms miss under thundering herd
  Memory: fast in RAM → 1000× slower when swapping to disk
  Concurrency: 1 connection works → 100 connections deadlock

THE PATTERN:
  Test: 100 records → 5ms ✓
  Staging: 1,000 records → 50ms ✓
  Production: 100,000 records → timeout ✗
```

**Fix**: Test at 10× expected production load. Explicitly ask: "what happens when the cache is cold?" and "what if this grows 10×?" Add circuit breakers and graceful degradation — fail fast, not slow.
