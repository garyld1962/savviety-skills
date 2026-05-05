# Go Review — Report Format

---

## Template

```
## Go Review — [branch or description]
[N files reviewed · N findings: N blocking, N non-blocking, N discussion]

---

### Blocking

#### `internal/api/handler.go:112` — Goroutine leak
**Found**: `go func() { result := <-resultChan; process(result) }()`
**Risk**: No exit path if resultChan is never written to. Goroutine lives forever — memory grows until OOM.
**Fix**: Add context select: `select { case r := <-resultChan: process(r); case <-ctx.Done(): return }`

#### `pkg/client/http.go:23` — `http.DefaultClient` used
**Found**: `resp, err := http.DefaultClient.Do(req)`
**Risk**: No timeout set. Hangs indefinitely on slow servers, exhausts goroutine pool under load.
**Fix**: `client := &http.Client{Timeout: 30 * time.Second}; resp, err := client.Do(req)`

---

### Non-blocking

#### `internal/db/queries.go:67` — Missing `defer cancel()`
**Found**: `ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)`
**Impact**: Context leak — resources attached to this context are never released if cancel is not called.
**Suggestion**: Add `defer cancel()` on the line immediately after.

---

### Discussion

#### `internal/service/user.go:8` — Single-method interface
**Found**: `type UserFetcher interface { GetUser(id string) (*User, error) }`
**Note**: Single-method interfaces are idiomatic Go (io.Reader style). Worth discussing whether the abstraction is needed yet or whether the concrete type suffices.

---

### Looks Good
- Error wrapping with `fmt.Errorf("...: %w", err)` throughout `pkg/auth/` — correct context chain
[or: All N remaining checks passed.]
```

---

## Formatting Rules

**Found field**: exact line from the diff. Max 3 lines; append `(N total — showing 3)` if more.

**Risk/Fix field** (blocking): state the production consequence, then the concrete fix. Show corrected code.

**Impact/Suggestion field** (non-blocking): frame as reliability gap. Show the fix, not a description of it.

**No commands in the report**: show findings, not the grep that found them.

**No preamble**: start directly with `## Go Review` header.

**Collapse passed checks**: if more than 8 checks passed with no findings, emit `All N remaining checks passed.`

**Skip test files in summary**: `*_test.go` findings only appear if Tier 1 blocking. Do not list test files in passed checks.

**Empty diff**: emit `No Go concerns — no .go changes.` and stop.

---

## Comment Style

- **Blocking**: state the production consequence. "Goroutine lives forever" beats "missing exit path."
- **Non-blocking**: name the reliability gap. "No cancellation propagation" beats "missing context."
- **Discussion**: acknowledge the author may have good reasons. "Worth discussing" beats "you should."
- Never: "you should have", "this is wrong", "why did you". The code is the subject, not the author.
