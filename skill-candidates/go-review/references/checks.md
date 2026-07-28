# Go Review — Checks

All checks run against added lines only (see SKILL.md Step 2 for extraction command).

---

## Tier 1 — Auto-Flag (Will Fail in Production)

Run against all changed `.go` files.

### Ignored Error (Blank Identifier on Error Return)

```bash
grep -nE "^\s*_\s*,?\s*=\s*\w+\(|^\s*_\s*=\s*\w+\(" <file> | grep -v "//\s*intentionally\|//\s*best.effort\|//\s*ignore" | head -5
```

Flag `_ = someCall()` or `_, _ = someCall()` with no explanatory comment. Silent failures are how production goes wrong without logs.

### Unchecked Error in Two-Value Return

```bash
grep -nE "^\s*\w+,\s*_\s*:?=\s*\w+\(" <file> | grep -v "//\s*err\|_test\.go" | head -5
```

Flag `val, _ := call()` where the blank identifier is in the error position. Requires context: verify the second return is actually an error type.

### Naked `panic` in Non-Test File

```bash
grep -nE "^\s*panic\(" <file> | head -5
```

Flag any `panic(` call. Skip matches in `*_test.go`. Check context: `panic` in `init()` or package-level variable initialization is borderline acceptable; flag anything in request handlers or business logic.

### Goroutine Started with No Exit Path

```bash
grep -nE "^\s*go\s+(func|[a-zA-Z])" <file> | head -10
```

For each goroutine launch, check ±20 lines for a `ctx.Done()` select case, `WaitGroup`, `done` channel, or bounded lifetime. Flag goroutines with no visible exit mechanism. This is a leak.

### `http.DefaultClient` Used

```bash
grep -n "http\.DefaultClient\b" <file> | head -5
```

Flag every match. `http.DefaultClient` has no timeout and will hang indefinitely on slow or unresponsive servers.

### `&http.Client{}` Without Timeout

```bash
grep -nE "&http\.Client\{[^}]*\}" <file> | grep -v "Timeout" | head -5
```

Flag `http.Client{}` struct literals with no `Timeout` field.

### Hardcoded Credentials or API Keys

```bash
grep -nEi "(password|apikey|api_key|secret|token)\s*[:=]\s*\"[^\"]{4,}\"" <file> | grep -v "//\|os\.Getenv\|env\." | head -5
```

Flag string literals assigned to credential-named variables. Always blocking.

### SQL Query with String Concatenation (Injection Risk)

```bash
grep -nE "(Query|Exec|QueryRow)\s*\([^,)]*\+" <file> | head -5
```

Flag SQL calls where the query string is built with `+` concatenation. Use parameterized queries instead.

---

## Tier 2 — Judgment Required

Apply to non-test `.go` files only.

### Context Not Propagated to DB/HTTP Calls

```bash
grep -nE "\.(Query|QueryRow|Exec|Get|Post|Do)\s*\(" <file> | grep -v "Context\|Ctx\|ctx" | head -5
```

Flag DB and HTTP calls with no context argument. Allows no cancellation or deadline propagation. Skip if the function signature shows no context available.

### Mutex Copied by Value

```bash
grep -nE "func\s+\w+\s*\(\s*\w+\s+\w*(Mutex|RWMutex|WaitGroup)" <file> | grep -v "\*" | head -5
```

Flag function parameters that receive a `sync.Mutex`, `sync.RWMutex`, or `sync.WaitGroup` by value (no `*` pointer). Copying a mutex copies its lock state — a data race.

### `time.Sleep` in Production Code

```bash
grep -nE "time\.Sleep\s*\(" <file> | head -5
```

Flag in non-test files. `time.Sleep` blocks a goroutine with no cancellation. Use `time.After` with a select and context cancellation instead.

### `context.WithTimeout` / `context.WithCancel` Without `defer cancel()`

```bash
grep -nE "context\.(WithTimeout|WithCancel|WithDeadline)\(" <file> | head -10
```

For each match, check ±5 lines for a `defer cancel()` call. Flag if missing — context leak causes goroutine and resource leaks.

---

## Tier 3 — Discussion

### Large Struct Passed by Value

```bash
grep -nE "func\s+\w+\s*\(\s*\w+\s+[A-Z]\w{10,}\b[^*]" <file> | grep -v "\*\|interface\b" | head -5
```

Flag large structs (heuristic: type name over 10 chars, no pointer) passed by value. Discuss: copying is fine for small structs, but consider pointer for anything with multiple fields.

### Single-Method Interface

```bash
grep -nE -A3 "type\s+\w+\s+interface\s*\{" <file> | head -20
```

Flag interfaces with exactly one method. Discussion point: single-method interfaces are idiomatic in Go (`io.Reader`, `io.Writer`), but ask whether the abstraction is needed yet.

### `init()` Function with Side Effects

```bash
grep -nE "^func init\(\)" <file> | head -5
```

Flag `init()` functions. Discussion: initialization side effects in `init()` are invisible to callers, make testing hard, and create initialization-order dependencies.
