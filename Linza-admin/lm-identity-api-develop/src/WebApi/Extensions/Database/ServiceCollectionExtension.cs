using Microsoft.EntityFrameworkCore;
using Provider.Database.Context;

namespace WebApi.Extensions.Database;

public static class ServiceCollectionExtension
{
    private const string ConnectionStringName = "IdentityData";

    public static IServiceCollection AddDatabase(
        this IServiceCollection services,
        IConfiguration config)
    {
        services.AddDbContext<IdentityDbContext>(options =>
        {
            options.UseNpgsql(
                config.GetConnectionString(ConnectionStringName),
                providerOptions => providerOptions.CommandTimeout(60)
            );
        });

        return services;
    }
}
