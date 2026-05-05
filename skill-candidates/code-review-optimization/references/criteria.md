# Code Review: Optimization — Criteria

---

## Dispositions

| Disposition | Meaning | PR Action |
|-------------|---------|-----------|
| **Blocking** | Must be fixed before merge. Risk of data loss, memory exhaustion, or silent behavior change. | Request changes |
| **Non-blocking** | Should be fixed, but does not stop the merge. Author should address in a follow-up. | Comment with suggestion |
| **Discussion** | Tradeoff worth acknowledging. No required action — author may have good reasons. | Comment as FYI |
| **Praise** | Good optimization decision worth calling out positively. | Inline compliment |

---

## Disposition by Check

### Blocking

| Check | Why |
|-------|-----|
| Unbounded cache | Will cause OOM in production over time. No safe workaround. |
| Await in forEach | Silent correctness bug — errors are swallowed, order not guaranteed. |
| Event listener without cleanup | Memory leak in long-running sessions. |
| Hidden side effect (sync→async refactor removing logging/events) | Behavioral regression. Downstream systems may depend on it. |
| Optimization without test coverage on changed logic | No safety net — refactor cannot be verified. |

### Non-blocking

| Check | Why |
|-------|-----|
| Sequential await in loop | Performance issue, not a correctness issue. Worth fixing soon. |
| Full library import (lodash, moment) | Bundle size impact — low urgency unless at budget. |
| String concat in loop | O(n²) string performance — only matters at scale. |
| DOM query in loop | Performance regression — low severity in most UI work. |
| Regex creation in loop | Avoidable allocation — non-critical unless in a hot path. |
| Sync file operations in non-startup code | Event loop blocking — matters under load. |

### Discussion

| Check | Why |
|-------|-----|
| Nested loops | May be intentional; depends on data size. Ask: what's n? |
| Direct raw SQL bypassing ORM | Performance vs. coupling tradeoff. Not wrong, but worth naming. |
| Premature abstraction signals (5+ optional params) | Rule of Three: wait for the third use case before generalizing. |
| Dependency version unlock | Stability vs. freshness tradeoff. |
| Console.log interpolation in src/ | Should use structured logger, but cosmetic in most cases. |

---

## Scope Rules

**Do not flag**:
- Issues in `*.test.*`, `*.spec.*`, `__tests__/` (except critical/blocking)
- Issues in `dist/`, `build/`, `.next/`, `*.generated.*`
- Issues in lines not present in the diff (pre-existing code)
- False positives where context makes the pattern intentional (see Tier 2 caveats)

**Do flag (even outside src/)**:
- Unbounded cache anywhere
- Await in forEach anywhere
- Uncleared event listeners anywhere

