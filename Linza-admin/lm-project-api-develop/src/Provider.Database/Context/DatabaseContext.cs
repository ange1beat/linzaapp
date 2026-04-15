using Microsoft.EntityFrameworkCore.Storage;
using Microsoft.EntityFrameworkCore;
using System.Reflection;

namespace Provider.Database.Context;

public class DatabaseContext : DbContext
{
    protected DatabaseContext() : base()
    {
    }

    public DatabaseContext(DbContextOptions<DatabaseContext> options) : base(options)
    {
    }

    public void Migrate()
    {
        Database.Migrate();
    }

    public IDbContextTransaction Transaction()
    {
        return base.Database.BeginTransaction();
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfigurationsFromAssembly(
            Assembly.GetAssembly(GetType())!
        );

        base.OnModelCreating(modelBuilder);
    }
}
