# Go Review — Criteria

---

## Dispositions

| Disposition | Meaning | PR Action |
|-------------|---------|-----------|
| **Blocking** | Will cause production failure, data loss, security vulnerability, or goroutine/resource leak | Request changes |
| **Non-blocking** | Should fix; doesn't stop merge. Reliability or correctness gap worth closing. | Comment with suggestion |
| **Discussion** | Tradeoff; author may have good reasons. Worth naming. | Comment as FYI |
| **Praise** | Good idiomatic decision worth calling out | Inline compliment |

---

## Disposition by Check

### Blocking

| Check | Why |
|-------|-----|
| Ignored error (blank identifier) | Silent failure. The operation failed; the code continues as if it succeeded. |
| `panic` in request handler / business logic | One bad request crashes the entire process. Must be recovered or converted to error return. |
| Goroutine leak (no exit path) | Memory grows without bound. OOM after hours/days. Invisible until it's too late. |
| `http.DefaultClient` or `&http.Client{}` without timeout | Hangs indefinitely on slow server. Exhausts goroutine pool under load. |
| Hardcoded credentials | Secret exposure in source control, logs, error messages. |
| SQL string concatenation | SQL injection vulnerability. |

### Non-blocking

| Check | Why |
|-------|-----|
| Context not propagated to DB/HTTP | No cancellation or deadline. Requests outlive their callers. Degrades under load. |
| Mutex copied by value | Race condition. The copied mutex is a different lock — protection is broken. |
| `time.Sleep` in production | No cancellation. Goroutine is unresponsive to shutdown for the sleep duration. |
| Missing `defer cancel()` | Context leak — goroutines and resources attached to the context are never released. |
| Unchecked error (blank second return) | Silent failure on error path. |

### Discussion

| Check | Why |
|-------|-----|
| Large struct by value | Copying cost. Worth discussing; small structs are fine by value. |
| Single-method interface | May be premature abstraction, or may be perfect Go idiom. Context matters. |
| `init()` with side effects | Hidden initialization order; makes testing harder. Worth naming. |

---

## Scope Rules

**Do not flag**:
- Issues in `vendor/`
- Issues in lines not in the diff (pre-existing code)
- `panic` in `*_test.go` files
- `time.Sleep` in `*_test.go` files
- False positives where a comment explicitly documents intentional ignore (e.g., `// best-effort cleanup`)

**Always flag regardless of file**:
- Hardcoded credentials
- Goroutine leaks
- `http.DefaultClient`
- SQL injection via string concatenation
