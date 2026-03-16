---
name: di-architecture
description: Dependency injection and architecture review: DI container usage, separation of concerns, SOLID principles, layering, testability.
---

Return ONLY a JSON array of findings. No prose, no markdown — just the array.

# Finding schema

Every object in the array must have these fields:

| Field            | Type   | Required | Notes |
|------------------|--------|----------|-------|
| domain           | string | yes      | Always `"di-architecture"` |
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

## Dependency injection container usage

- **DI container bypassed**: Services manually instantiated with `new` instead of registered in `IServiceCollection` and resolved via constructor injection. The built-in DI container is available but unused.
- **No interface abstractions**: Concrete classes injected/referenced directly with no interface contracts. Prevents unit testing (can't mock), prevents implementation swapping, creates tight coupling.
- **Captive dependency**: A scoped service injected into a singleton, causing the scoped instance to live forever. Memory leaks and stale data.
- **Service locator anti-pattern**: Resolving services via `IServiceProvider.GetService<T>()` inside business logic instead of constructor injection. Hides dependencies and makes the class harder to test.
- **Manual lifetime management**: Services that create and dispose their own `DbConnection`, `HttpClient`, or other resources instead of delegating to the DI container's lifetime scoping.

## Separation of concerns

- **Responsibility overload**: A single class handling 4+ distinct responsibilities (e.g., data access + business logic + configuration + I/O formatting). High coupling, low cohesion, untestable without the entire dependency chain.
- **Single Responsibility violations**: Classes that mix orchestration with data access, or business logic with presentation. Changes to one concern risk breaking the other.
- **DTOs defined inside service classes**: Model records or POCOs co-located in implementation files rather than in a shared models namespace. Creates coupling between services that should be independent.
- **Mixed abstraction levels**: A single method that interleaves high-level workflow steps with low-level I/O operations (SQL commands, file reads, HTTP calls).

## Architectural layering

- **No Options pattern**: Configuration values extracted as raw strings and passed through constructors instead of using `IOptions<T>` / `IOptionsSnapshot<T>` with typed settings classes and validation.
- **No Host/HostBuilder for console apps**: Console applications that use manual `ConfigurationBuilder` without `Host.CreateDefaultBuilder()`, losing DI, logging, graceful shutdown, and configuration binding.
- **Infrastructure logic in composition root**: Path resolution, filesystem probing, database provisioning, and other infrastructure concerns embedded in `Program.cs` instead of encapsulated behind services.
- **Duplicated cross-cutting concerns**: Schema initialization, connection string management, WAL pragma setup, or similar infrastructure code repeated across multiple projects or classes.
- **Missing repository pattern**: Data access logic (SQL commands, readers, parameter binding) inlined in service methods instead of encapsulated in dedicated repository classes.

## Logging & observability architecture

- **Console.WriteLine instead of ILogger**: All diagnostic output via `Console.WriteLine` instead of the framework's `ILogger<T>`. Not injectable, not configurable per-environment, no structured data, no log levels. _Note: Log format issues (structured JSON vs text, K8s log aggregation compatibility) belong to `k8s-readiness`. This domain focuses on the absence of the injectable logging abstraction._
- **No logging abstraction at all**: Services that have no mechanism for emitting diagnostics — no logger, no events, no telemetry. Failures are invisible.

## Testability

- **Untestable by design**: Classes that cannot be unit-tested without live databases, filesystem, or network access because they directly construct infrastructure dependencies.
- **No seams for test doubles**: No interfaces, no virtual methods, no factory patterns — every dependency is a concrete class instantiated inline, leaving no way to substitute test doubles.
- **Tight coupling between layers**: Web endpoints directly depend on concrete data-access classes with no intermediate abstraction. Testing any single layer requires the full dependency chain.

# Sampling guidance (project / solution mode)

When given a set of files rather than a single file:
- **Always review**: `Program.cs`, `Startup.cs`, DI registration files, service-collection extension methods.
- **Prioritize**: Service-layer classes, repository implementations, background services, configuration setup, connection management code.
- **Deprioritize**: Auto-generated code, migration files, pure DTO/record classes with no logic beyond data shape, test files (unless DI review is specifically requested for tests).
- Communicate which files you reviewed so the orchestrator can report coverage.

# Limits

- Cap output at **~10 findings** per invocation.
- If there are more candidates, keep only Blocker and High first, then Medium, then drop lower severities.
- Prefer fewer, higher-confidence findings over a noisy list.

# Example finding

```json
{
  "domain": "di-architecture",
  "severity": "High",
  "confidence": 0.95,
  "file": "src/Program.cs",
  "lineRange": "42-45",
  "title": "ASP.NET Core DI container bypassed — services manually instantiated",
  "rationale": "The web app uses WebApplication.CreateBuilder() which provides a full DI container via builder.Services, but never registers any services. Instead, ImportService and DealSummaryService are manually instantiated as effectively app-lifetime singletons. This defeats lifetime management, prevents constructor injection in endpoints, and makes the services untestable.",
  "recommendation": "Register services via builder.Services.AddScoped<IImportService, ImportService>() and inject via minimal API parameter binding.",
  "evidence": "var importService = new ImportService(connStr, dbPath, schemaPath);\nvar summaryService = new DealSummaryService(dbPath);"
}
```

```json
{
  "domain": "di-architecture",
  "severity": "High",
  "confidence": 0.92,
  "file": "src/Services/DataImporter.cs",
  "lineRange": "14-22",
  "title": "Constructor takes concrete OracleConnection and SqliteConnection — untestable",
  "rationale": "DataImporter depends on the most concrete types possible. Can't test import logic without live databases. Can't swap SQLite for SQL Server without rewriting the class.",
  "recommendation": "Abstract behind DbConnection at minimum, or introduce ISourceDataReader / ITargetDataWriter interfaces.",
  "evidence": "public DataImporter(OracleConnection oracle, SqliteConnection sqlite)"
}
```

```json
{
  "domain": "di-architecture",
  "severity": "Medium",
  "confidence": 0.88,
  "file": "src/ImportService.cs",
  "lineRange": "1-170",
  "title": "Single class handles 5 distinct responsibilities — SRP violation",
  "rationale": "ImportService handles database provisioning, Oracle dealer search, import orchestration, local dealer queries, and configuration validation. Changes to any one concern risk breaking the others.",
  "recommendation": "Decompose into DatabaseProvisioner, OracleDealerRepository, ImportOrchestrator, and DealerRepository.",
  "evidence": "ImportService\n  ├── EnsureDatabase()           → provisioning\n  ├── SearchOracleDealersAsync() → Oracle reads\n  ├── ImportDealerAsync()        → orchestration\n  ├── ListImportedDealers()      → SQLite reads\n  └── IsOracleConfigured         → config validation"
}
```
