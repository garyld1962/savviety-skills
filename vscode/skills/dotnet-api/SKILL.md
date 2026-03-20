---
name: dotnet-api
description: "ASP.NET API patterns — minimal APIs, controllers, middleware, configuration, health checks, OpenAPI"
---

# .NET API Patterns

Opinionated patterns for ASP.NET APIs. Use when writing or reviewing HTTP API code.

## Prefer Minimal APIs for New Endpoints

```csharp
// PREFERRED — minimal API
app.MapGet("/api/jobs/{id}", async (Guid id, IJobService service) =>
{
    var job = await service.GetByIdAsync(id);
    return job is null ? Results.NotFound() : Results.Ok(job);
});

// ACCEPTABLE — controller (for complex endpoints with many actions)
[ApiController]
[Route("api/[controller]")]
public class JobsController : ControllerBase { ... }
```

Use controllers when you have 5+ related endpoints that share filters, model binding, or auth attributes. For 1-3 endpoints, minimal APIs are simpler.

## Dependency Injection

- Register services in `Program.cs` or a `ServiceCollectionExtensions` class — NOT scattered across files.
- Use `AddScoped<TInterface, TImplementation>()` for request-scoped services.
- Use `AddSingleton` only for stateless, thread-safe services.
- Never resolve from `IServiceProvider` directly in application code — inject through constructors.

```csharp
// CORRECT — extension method keeps Program.cs clean
public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddJobServices(this IServiceCollection services)
    {
        services.AddScoped<IJobService, JobService>();
        services.AddScoped<IJobRepository, JobRepository>();
        return services;
    }
}

// In Program.cs
builder.Services.AddJobServices();
```

## Configuration

- Bind config sections to strongly-typed classes with `IOptions<T>`.
- Never read `IConfiguration` directly in service classes.
- Validate configuration at startup with `ValidateOnStart()`.

```csharp
builder.Services
    .AddOptions<DatabaseOptions>()
    .Bind(builder.Configuration.GetSection("Database"))
    .ValidateDataAnnotations()
    .ValidateOnStart();
```

## Error Handling

- Use `ProblemDetails` for API error responses (RFC 9457).
- Register a global exception handler — do NOT try-catch in every endpoint.
- Use custom exception types for domain errors.

```csharp
// Program.cs
app.UseExceptionHandler();
app.UseStatusCodePages();

// For minimal APIs — use Results.Problem()
return Results.Problem(
    statusCode: 404,
    title: "Job not found",
    detail: $"No job with ID {id}");
```

## Request Validation

- Use FluentValidation or DataAnnotations — NOT manual if-checks in handlers.
- Validate as early as possible (endpoint filter or middleware).

## Health Checks

Every API must have health checks:

```csharp
builder.Services.AddHealthChecks()
    .AddNpgSql(connectionString)     // database
    .AddUrlGroup(new Uri(dep), "dependency-name");  // downstream

app.MapHealthChecks("/healthz");
app.MapHealthChecks("/readyz", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready")
});
```

## OpenAPI / Swagger

- Always add OpenAPI metadata to endpoints.
- Use `WithName()`, `WithTags()`, `Produces<T>()` on minimal APIs.

```csharp
app.MapGet("/api/jobs/{id}", handler)
    .WithName("GetJobById")
    .WithTags("Jobs")
    .Produces<JobDto>(200)
    .Produces(404);
```
