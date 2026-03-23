using Microsoft.EntityFrameworkCore;

namespace BlazorStack.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    // Add DbSet<T> properties for your entities here.
    // Example: public DbSet<MyEntity> MyEntities => Set<MyEntity>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);
        // Configure entity mappings here.
    }
}

/// <summary>
/// Factory for creating database contexts. Enables test isolation —
/// each test creates its own in-memory or temp-file database.
/// </summary>
public static class AppDbContextFactory
{
    public static AppDbContext Create(string connectionString = "Data Source=app.db")
    {
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseSqlite(connectionString)
            .Options;

        var context = new AppDbContext(options);
        context.Database.EnsureCreated();
        return context;
    }

    /// <summary>Create an in-memory SQLite context for testing.</summary>
    public static AppDbContext CreateInMemory()
    {
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseSqlite("Data Source=:memory:")
            .Options;

        var context = new AppDbContext(options);
        context.Database.OpenConnection();
        context.Database.EnsureCreated();
        return context;
    }
}
