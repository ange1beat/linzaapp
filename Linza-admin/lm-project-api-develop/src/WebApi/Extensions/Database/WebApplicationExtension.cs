using Provider.Database.Context;

namespace WebApi.Extensions.Database;

public static class WebApplicationExtension
{
    public static void MigrateDatabase(this WebApplication app)
    {
        using var scope = app.Services
            .GetRequiredService<IServiceScopeFactory>()
            .CreateScope();

        scope.ServiceProvider
            .GetRequiredService<DatabaseContext>()
            .Migrate();
    }
}
