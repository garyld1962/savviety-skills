---
name: async-safety
description: Async/await safety review: deadlocks, blocking calls, CancellationToken propagation, concurrency hazards.
---

Return ONLY a JSON array of findings. No prose, no markdown — just the array.

# Finding schema

Every object in the array must have these fields:

| Field            | Type   | Required | Notes |
|------------------|--------|----------|-------|
| domain           | string | yes      | Always `"async-safety"` |
| severity         | string | yes      | One of: Blocker, High, Medium, Low, Info |
| confidence       | number | yes      | 0.00–1.00 (do not emit below 0.50) |
| file             | string | yes      | Repo-relative path |
| lineRange        | string | no       | e.g. `"42-58"` — omit only if file-wide |
| title            | string | yes      | ≤120 chars |
| rationale        | string | yes      | Root cause, risk, impact |
| recommendation   | string | yes      | Concrete fix |
| evidence         | string | yes      | Short code snippet or reference |
| suggestedPatch   | string | no       | Unified-diff style fix |

No extra fields are allowed (`additionalProperties: false`).

# Severity rubric

- **Blocker**: Likely to cause production incident, data loss, broken builds, or a serious security issue.
- **High**: Serious bug risk, security weakness, major reliability/perf issue, hard-to-debug behavior.
- **Medium**: Real issue but with mitigations; maintainability/correctness risk in edge cases.
- **Low**: Minor maintainability/clarity improvement; should not block merges.
- **Info**: Observation, question, or suggestion without strong evidence.

# Confidence calibration

- 0.90–1.00: Clear evidence in code — you can point to the exact line(s).
- 0.70–0.89: Strong signals, some assumptions about runtime behavior.
- 0.50–0.69: Plausible issue, needs confirmation from the developer.
- Below 0.50: **Do not emit.** Discard silently. Do not speculate.

# Domain focus areas

- **Sync-over-async deadlocks**: `.Result`, `.Wait()`, `.GetAwaiter().GetResult()` called on async paths — especially in ASP.NET controllers, middleware, or UI contexts where a `SynchronizationContext` exists.
- **Missing CancellationToken propagation**: Async methods that accept a `CancellationToken` but don't pass it to downstream calls, or public async APIs that don't accept one at all.
- **Fire-and-forget tasks**: `Task` returned by an async call but not awaited, observed, or logged — exceptions will be silently swallowed.
- **Unbounded concurrency**: `Task.WhenAll` over an unbounded collection without throttling (e.g. `SemaphoreSlim`), `Parallel.ForEach` on server-side code.
- **Misuse of Task.Run in server code**: Wrapping sync work in `Task.Run` inside ASP.NET request handlers just to make it "async" — wastes a thread-pool thread.
- **Missing ConfigureAwait(false)**: In library code (not app code), missing `ConfigureAwait(false)` can cause context-capture overhead or subtle deadlocks.
- **Timeout gaps**: Long-running I/O calls without `CancellationTokenSource` timeout or `HttpClient.Timeout`.

# Sampling guidance (project / solution mode)

When given a set of files rather than a single file:
- **Always review**: Controllers, middleware, background services (`IHostedService`, `BackgroundService`), message handlers.
- **Prioritize**: Service-layer classes with `async` methods, HTTP client wrappers, database access layers.
- **Deprioritize**: Pure synchronous utility classes, DTOs, models, auto-generated code.
- Communicate which files you reviewed so the orchestrator can report coverage.

# Limits

- Cap output at **~10 findings** per invocation.
- If there are more candidates, keep only Blocker and High first, then Medium, then drop lower severities.
- Prefer fewer, higher-confidence findings over a noisy list.

# Example finding

```json
{
  "domain": "async-safety",
  "severity": "Blocker",
  "confidence": 0.95,
  "file": "src/Controllers/OrderController.cs",
  "lineRange": "31-31",
  "title": ".Result used in async controller action — deadlock risk",
  "rationale": "Calling .Result on an incomplete Task inside an ASP.NET controller synchronously blocks the request thread while the continuation needs the same SynchronizationContext, causing a classic deadlock under load.",
  "recommendation": "Change the method to `async Task<IActionResult>` and `await` the call instead of using `.Result`.",
  "evidence": "var order = _orderService.GetOrderAsync(id).Result; // line 31"
}
```
