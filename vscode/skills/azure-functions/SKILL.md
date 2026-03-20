---
name: azure-functions
description: "Azure Functions patterns — isolated worker model, triggers, bindings, DI, configuration, error handling"
---

# Azure Functions Patterns

Opinionated patterns for Azure Functions. Always use the **isolated worker model** (not in-process).

## Project Setup

```
MyFunction/
├── Program.cs              # Host builder, DI, config
├── Functions/
│   ├── HttpTriggers.cs     # HTTP-triggered functions
│   ├── TimerTriggers.cs    # Timer/cron functions
│   └── QueueTriggers.cs    # Queue/event triggers
├── Services/               # Business logic (injectable)
├── Models/                 # DTOs, request/response types
└── host.json
```

Group functions by trigger type, not by domain. Business logic lives in `Services/`, NOT in function classes.

## Function Classes Are Thin

Function classes are entry points — they validate input, call a service, and return a response. No business logic.

```csharp
// CORRECT — thin function, logic in service
public class JobFunctions
{
    private readonly IJobService _jobService;
    public JobFunctions(IJobService jobService) => _jobService = jobService;

    [Function("ProcessJob")]
    public async Task Run(
        [QueueTrigger("jobs")] JobMessage message,
        FunctionContext context)
    {
        var logger = context.GetLogger<JobFunctions>();
        logger.LogInformation("Processing job {JobId}", message.JobId);
        await _jobService.ProcessAsync(message);
    }
}

// WRONG — business logic in function class
[Function("ProcessJob")]
public async Task Run([QueueTrigger("jobs")] JobMessage message, ...)
{
    var connection = new SqlConnection(...);  // NO — use DI
    await connection.ExecuteAsync(...);       // NO — use a service
}
```

## Dependency Injection

Use `Program.cs` with `HostBuilder`:

```csharp
var host = new HostBuilder()
    .ConfigureFunctionsWebApplication()
    .ConfigureServices((context, services) =>
    {
        services.AddOptions<DatabaseOptions>()
            .Bind(context.Configuration.GetSection("Database"));
        services.AddScoped<IJobService, JobService>();
    })
    .Build();

host.Run();
```

## Configuration

- Use `local.settings.json` for local dev (never commit).
- Use App Settings or Key Vault references in Azure.
- Bind to `IOptions<T>` — never read `Environment.GetEnvironmentVariable()` in service code.

## HTTP Triggers

```csharp
[Function("GetJob")]
public async Task<HttpResponseData> GetJob(
    [HttpTrigger(AuthorizationLevel.Function, "get", Route = "jobs/{id}")] HttpRequestData req,
    Guid id)
{
    var job = await _jobService.GetByIdAsync(id);
    if (job is null)
    {
        var notFound = req.CreateResponse(HttpStatusCode.NotFound);
        return notFound;
    }

    var response = req.CreateResponse(HttpStatusCode.OK);
    await response.WriteAsJsonAsync(job);
    return response;
}
```

## Timer Triggers

```csharp
[Function("CleanupExpiredJobs")]
public async Task Run([TimerTrigger("0 0 2 * * *")] TimerInfo timer, FunctionContext context)
{
    var logger = context.GetLogger<CleanupFunction>();
    if (timer.IsPastDue) logger.LogWarning("Timer is past due");

    var count = await _cleanupService.RemoveExpiredAsync();
    logger.LogInformation("Cleaned up {Count} expired jobs", count);
}
```

## Error Handling

- Log and rethrow in functions — let the runtime handle retries.
- Configure retry policies in `host.json`, not in code.
- Use `maxDequeueCount` for poison message handling on queues.

```json
// host.json
{
  "extensions": {
    "queues": {
      "maxDequeueCount": 3,
      "visibilityTimeout": "00:00:30"
    }
  }
}
```

## Testing

- Test services directly — do NOT test through function classes.
- Function classes are wiring — test them with integration tests if needed.
- Mock `FunctionContext` for unit tests using `TestFunctionContext` helper.
