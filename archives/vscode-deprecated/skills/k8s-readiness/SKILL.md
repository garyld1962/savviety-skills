---
name: k8s-readiness
description: Kubernetes readiness review: health probes, graceful shutdown, resource limits, structured logging, observability.
---

Return ONLY a JSON array of findings. No prose, no markdown — just the array.

# Finding schema

Every object in the array must have these fields:

| Field            | Type   | Required | Notes |
|------------------|--------|----------|-------|
| domain           | string | yes      | Always `"k8s-readiness"` |
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

## Health probes & graceful shutdown

- **Missing health checks**: No `/health` or `/ready` endpoint registered. Kubernetes cannot distinguish a healthy pod from a broken one, leading to traffic routed to unresponsive instances.
- **Liveness vs readiness conflation**: A single health endpoint used for both probes without separating dependency checks. A transient downstream outage (e.g. DB) triggers pod restarts instead of just removing the pod from the load balancer.
- **Missing startup probe consideration**: Slow-starting services (large DI graphs, migration steps, cache warm-up) with aggressive liveness timers get killed in a restart loop before they finish initializing.
- **Ungraceful shutdown**: No `IHostApplicationLifetime` / `CancellationToken` handling on SIGTERM. In-flight requests are dropped or background work is aborted mid-operation during rolling deployments. `Host.CreateDefaultBuilder` wires SIGTERM, but custom `Task.Run` or message consumers often ignore it.
- **Drain period mismatch**: Code that completes instantly on shutdown without draining queued work or allowing HTTP keep-alive connections to close. Kubernetes sends SIGTERM then waits `terminationGracePeriodSeconds` (default 30s) — if the app exits in 0s, in-flight requests from the Service are lost.

## Performance in a container

- **Unbounded thread / connection usage**: No limits on `HttpClient` connections, `SemaphoreSlim` concurrency, or `Parallel.ForEach` degree — the app will consume all CPU/memory in the pod's cgroup and get OOM-killed or throttled.
- **Server GC in small containers**: The default `ServerGC` mode is tuned for dedicated servers; in a container with ≤2 CPUs it can overshoot memory and trigger OOM kills. `WorkstationGC` or `GCHeapCount=1` may be more appropriate.
- **Missing resource hints in code**: Large buffer allocations (e.g. `new byte[10_000_000]`) or unconstrained caching that ignores the pod's memory limit. `Environment.ProcessorCount` returns the node's CPU count, not the pod's — use `System.Runtime.GCSettings` or `cgroup` awareness.
- **Cold-start amplification**: Lazy initialization of expensive resources (HTTP connections, DB pools, ML models) at first request instead of in `IHostedService.StartAsync`, causing readiness probe failures and request timeouts during scale-out.
- **Missing Kestrel tuning**: Default Kestrel limits (request body size, header count, concurrent connections) may be wrong for the workload. In K8s, the pod is behind an ingress/sidecar, so some limits can be tightened and idle timeouts aligned.

## Structured logging & diagnostics

- **Unstructured log output**: Using `Console.WriteLine`, string-concatenated messages, or `ILogger` with `$"interpolated {values}"` instead of message templates. Unstructured logs are nearly impossible to query in centralized log systems (ELK, Loki, Application Insights). _Note: The absence of `ILogger` as an architectural concern belongs to `di-architecture`. This domain focuses on log format and K8s log pipeline compatibility._
- **Missing correlation IDs**: No `Activity` / `IHttpContextAccessor.TraceIdentifier` propagated through log scopes. When a failure spans multiple services, there is no way to correlate the causal chain.
- **Excessive or insufficient log levels**: Logging request payloads or PII at `Information` level (noise + compliance risk), or catching exceptions and logging at `Debug` (silent failures in production where `Debug` is suppressed).
- **Missing exception details**: `catch (Exception ex) { _logger.LogError("Failed"); }` — the exception object is not passed to the logger, so stack traces, inner exceptions, and exception data are lost.
- **No startup / shutdown logging**: The service starts and stops without logging its version, configuration source, environment name, or health-check registration. When a pod restarts in a crash loop, operators have no context for what happened.

## Telemetry & distributed tracing

- **No OpenTelemetry / Application Insights SDK**: The service has no tracing or metrics instrumentation. Kubernetes liveness probes tell you a pod is alive, but without traces you cannot see *why* a request was slow or which downstream call failed.
- **Missing outbound trace propagation**: `HttpClient` calls not using `AddHttpClientInstrumentation()` or an equivalent delegating handler — trace context is not propagated to downstream services, breaking the distributed trace.
- **No custom metrics for business operations**: Only default runtime metrics (GC, thread pool) are exported. Key business counters (orders processed, queue depth, retry count) are missing, making capacity planning and alerting impossible.
- **Trace/metric exporter misconfiguration**: Hardcoded OTLP endpoint URLs or missing environment-variable-driven configuration (`OTEL_EXPORTER_OTLP_ENDPOINT`). In K8s, the collector sidecar/daemonset address must be configurable per namespace.
- **Missing `Activity.Source` registration**: Custom `ActivitySource` instances created but not registered with the OpenTelemetry SDK `AddSource()` — traces are silently dropped.

## Failure prediction & resilience

- **No retry / circuit-breaker on outbound calls**: HTTP or gRPC calls to other services without Polly / `Microsoft.Extensions.Http.Resilience` policies. A single downstream hiccup cascades into 5xx responses and pod restarts if the liveness probe calls the same path.
- **Missing timeout on external I/O**: Database queries, HTTP calls, or message-broker operations without explicit timeouts. Under network partition the thread blocks indefinitely, exhausting the thread pool and making the pod unresponsive.
- **Swallowed transient failures**: Catching exceptions and returning a default value without logging or incrementing a failure metric. The system silently degrades, and operators have no signal until users report data loss.
- **No dead-letter / poison-message handling**: Queue consumers that fail on a malformed message will retry indefinitely (crash loop) or silently drop the message. Either way, there is no alertable signal.
- **Missing readiness probe dependency checks**: The readiness endpoint returns healthy without verifying critical dependencies (DB, cache, message broker). Kubernetes routes traffic to a pod that cannot actually serve requests.
- **Unobserved background task failures**: `IHostedService` / `BackgroundService` implementations where an unhandled exception kills the background loop silently — the pod stays "alive" (liveness passes) but stops processing work.

# Sampling guidance (project / solution mode)

When given a set of files rather than a single file:
- **Always review**: `Program.cs`, `Startup.cs`, `appsettings.json`, `Dockerfile`, DI registration files, health-check registrations, any `IHostedService` / `BackgroundService` implementations.
- **Prioritize**: HTTP client configuration, middleware pipeline, logging setup, telemetry/OpenTelemetry bootstrapping, retry/resilience policy definitions, Kestrel configuration.
- **Deprioritize**: Pure DTOs, auto-generated code, migration files, unit test files (unless K8s integration tests are specifically requested).
- Communicate which files you reviewed so the orchestrator can report coverage.

# Limits

- Cap output at **~10 findings** per invocation.
- If there are more candidates, keep only Blocker and High first, then Medium, then drop lower severities.
- Prefer fewer, higher-confidence findings over a noisy list.

# Example finding

```json
{
  "domain": "k8s-readiness",
  "severity": "High",
  "confidence": 0.90,
  "file": "src/Program.cs",
  "lineRange": "12-34",
  "title": "No health-check endpoints registered — K8s cannot detect pod failures",
  "rationale": "The application does not call AddHealthChecks() or MapHealthChecks(). Without a health endpoint, Kubernetes liveness and readiness probes have nothing to target. A hung process or broken dependency will continue receiving traffic indefinitely.",
  "recommendation": "Add `builder.Services.AddHealthChecks().AddCheck(\"self\", () => HealthCheckResult.Healthy())` and map separate endpoints: `app.MapHealthChecks(\"/healthz\", new() { Predicate = _ => false })` for liveness and `app.MapHealthChecks(\"/ready\")` for readiness with dependency checks.",
  "evidence": "var app = builder.Build(); // no AddHealthChecks() or MapHealthChecks() in startup"
}
```

```json
{
  "domain": "k8s-readiness",
  "severity": "High",
  "confidence": 0.88,
  "file": "src/Services/PaymentWorker.cs",
  "lineRange": "18-45",
  "title": "BackgroundService swallows exceptions — silent work stoppage",
  "rationale": "ExecuteAsync catches Exception and logs at Debug level without rethrowing or signaling the health check. If the processing loop exits, the pod stays alive (liveness passes) but stops consuming messages. Operators get no alert until the queue backs up.",
  "recommendation": "Log at Error level, increment a failure metric, and either rethrow (to let the host restart the service) or set a health-check flag to unhealthy so the readiness probe removes the pod from the load balancer.",
  "evidence": "catch (Exception ex) { _logger.LogDebug(\"Worker error\"); } // line 38 — exception object not passed, logged at Debug"
}
```

```json
{
  "domain": "k8s-readiness",
  "severity": "Medium",
  "confidence": 0.82,
  "file": "src/Program.cs",
  "lineRange": "8-8",
  "title": "No structured logging configured — log aggregation will fail",
  "rationale": "Logging uses default console provider with no JSON formatter. In Kubernetes, stdout is captured by the container runtime and forwarded to a log aggregator (Fluentd, Promtail). Unstructured text lines break multi-line log parsing and make field-level queries impossible.",
  "recommendation": "Add `.AddJsonConsole()` or configure OpenTelemetry log exporter: `builder.Logging.AddOpenTelemetry(o => o.AddOtlpExporter())`. Ensure all log calls use message templates, not string interpolation.",
  "evidence": "builder.Logging.AddConsole(); // default unstructured format"
}
```
