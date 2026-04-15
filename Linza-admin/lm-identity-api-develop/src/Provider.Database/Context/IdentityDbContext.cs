using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Storage;
using Npgsql;
using System.Reflection;

namespace Provider.Database.Context;

public class IdentityDbContext : DbContext
{
    public IdentityDbContext()
    {
    }

    public IdentityDbContext(DbContextOptions<IdentityDbContext> options)
        : base(options)
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

    public bool IsUniqueViolationError(DbUpdateException exc, string columnName)
    {
        return exc.InnerException is PostgresException psqlExc &&
            psqlExc.SqlState == PostgresErrorCodes.UniqueViolation &&
            psqlExc.ConstraintName!.Contains(columnName, StringComparison.OrdinalIgnoreCase);
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfigurationsFromAssembly(
            Assembly.GetAssembly(GetType())!
        );

        base.OnModelCreating(modelBuilder);
    }
}
