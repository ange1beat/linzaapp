using Domain.Files;
using Domain.Projects;
using Domain.Projects.Favorites;
using Domain.Users;
using Provider.Database.Projects;
using Provider.Database.Projects.Favorites;
using Provider.FileSystem.Files;
using Provider.Identity.Users;
using System.Net;
using Domain.Projects.Membership;
using Polly;
using Polly.Extensions.Http;
using Provider.Database.Projects.Membership;
using WebApi.Models.Authentication.Guards;
using WebApi.Models.Files;
using WebApi.Models.Projects;
using WebApi.Models.Users;

namespace WebApi.Extensions.Application;

public static class ServiceCollectionExtension
{
    public static IServiceCollection AddApplicationServices(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        services.AddSingleton<IFsStorageSettings, FsStorageSettings>();
        services.AddSingleton<IFileStorage, FileSystemStorage>();

        services.AddSingleton<IResourceGuardSettings, ResourceGuardSettings>();
        services.AddSingleton<IResourceGuard, ResourceGuard>();

        services.AddSingleton<IProjectSettings, ProjectSettings>();
        services.AddSingleton<IFavoritesSettings, FavoritesSettings>();
        services.AddSingleton<IProjectValidationSettings, ProjectValidationSettings>();

        services.AddScoped<IProjects, Projects>();
        services.AddScoped<IFavoriteProjects, FavoriteProjects>();
        services.AddScoped<IProjectsMembership, ProjectsMembership>();

        services.AddUserClient(new UsersSettings(configuration));

        return services;
    }

    private static void AddUserClient(
        this IServiceCollection services,
        UsersSettings settings)
    {
        services
            .AddHttpClient<IUsers, Users>(options =>
            {
                options.BaseAddress = settings.ApiBaseUrl;
                options.Timeout = TimeSpan.FromSeconds(10);
            })
            .ConfigurePrimaryHttpMessageHandler(_ => new HttpClientHandler
            {
                AutomaticDecompression =
                    DecompressionMethods.GZip | DecompressionMethods.Deflate,
                ServerCertificateCustomValidationCallback = (_, _, _, _) => true
            })
            .AddPolicyHandler(HttpPolicyExtensions
                .HandleTransientHttpError()
                .WaitAndRetryAsync(2, retryAttempt =>
                    TimeSpan.FromSeconds(Math.Pow(2, retryAttempt))
                )
            )
            .AddPolicyHandler(HttpPolicyExtensions
                .HandleTransientHttpError()
                .CircuitBreakerAsync(5, TimeSpan.FromSeconds(30))
            )
            .SetHandlerLifetime(TimeSpan.FromMinutes(5));
    }
}
