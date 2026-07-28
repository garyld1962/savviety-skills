using BlazorStack.Data;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

// Database
var connectionString = builder.Configuration.GetConnectionString("Default") ?? "Data Source=app.db";
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlite(connectionString));

// CORS — allow the Blazor frontend during development
builder.Services.AddCors(options =>
    options.AddDefaultPolicy(policy =>
        policy.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()));

// ProblemDetails for structured error responses
builder.Services.AddProblemDetails();

var app = builder.Build();

// Ensure database is created
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.EnsureCreated();
}

app.UseCors();
app.UseExceptionHandler();

// Health check
app.MapGet("/health", () => Results.Ok(new { status = "healthy" }));

// TODO: Map your API endpoints here.
// Example:
// app.MapGet("/api/v1/items", async (AppDbContext db) => ...);

app.Run();
