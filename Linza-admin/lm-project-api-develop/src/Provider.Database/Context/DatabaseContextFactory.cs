using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;

namespace Provider.Database.Context;

public class DatabaseContextFactory : IDesignTimeDbContextFactory<DatabaseContext>
{
    private const string ConnectionStringEnvName = "ConnectionStrings__PsqlDb";

    public DatabaseContext CreateDbContext(string[] args)
    {
        string connectionString = Environment.GetEnvironmentVariable(ConnectionStringEnvName)
            ?? string.Empty;

        if (args.Length > 0)
        {
            connectionString = args[0];
        }

        var dbContextOptions = new DbContextOptionsBuilder<DatabaseContext>()
            .UseNpgsql(
                connectionString,
                providerOptions => providerOptions.CommandTimeout(60)
            )
            .Options;

        return new DatabaseContext(dbContextOptions);
    }
}
