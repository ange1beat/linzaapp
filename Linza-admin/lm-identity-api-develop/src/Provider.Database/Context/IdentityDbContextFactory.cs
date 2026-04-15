using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;

namespace Provider.Database.Context;

public class IdentityDbContextFactory : IDesignTimeDbContextFactory<IdentityDbContext>
{
    private const string CONNECTION_STRING_ENV_NAME = "ConnectionStrings__IdentityData";

    public IdentityDbContext CreateDbContext(string[] args)
    {
        string connectionString = Environment.GetEnvironmentVariable(CONNECTION_STRING_ENV_NAME)
            ?? string.Empty;

        if (args.Any())
        {
            connectionString = args[0];
        }

        Console.WriteLine(connectionString);

        DbContextOptions<IdentityDbContext> dbContextOptions =
            new DbContextOptionsBuilder<IdentityDbContext>()
                .UseNpgsql(connectionString, options => options.CommandTimeout(60))
                .Options;

        return new IdentityDbContext(dbContextOptions);
    }
}
