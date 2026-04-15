using Domain.Auth;
using Domain.Auth.Factors;
using Domain.Auth.Identity;
using Domain.Auth.Password;
using Domain.Auth.Recovery;
using Domain.Auth.Tokens;
using Domain.Cellular;
using Domain.Email;
using Domain.Files;
using Domain.Messages;
using Domain.Projects;
using Domain.Tenants;
using Domain.Users;
using Domain.Users.Challenges;
using Domain.Users.Invitations;
using Microsoft.AspNetCore.Identity;
using Polly;
using Polly.Extensions.Http;
using Polly.Timeout;
using Provider.Cellular;
using Provider.Database.Auth;
using Provider.Database.Auth.Factors;
using Provider.Database.Auth.Recovery;
using Provider.Database.Auth.Tokens;
using Provider.Database.Messages;
using Provider.Database.Tenants;
using Provider.Database.Users;
using Provider.Database.Users.Challenges;
using Provider.Database.Users.Invitations;
using Provider.Email;
using Provider.FileSystem;
using Provider.Projects;
using System.Net;
using System.Net.Http.Headers;
using WebApi.Models.Auth;
using WebApi.Models.Files;
using WebApi.Models.Invitations;
using WebApi.Models.Projects;
using WebApi.Models.Users;

namespace WebApi.Extensions.Application;

public static class ServiceCollectionExtension
{
    public static IServiceCollection AddApplicationServices(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        services.Configure<PasswordOptions>(options =>
        {
            options.RequireDigit = true;
            options.RequireLowercase = true;
            options.RequireNonAlphanumeric = true;
            options.RequireUppercase = true;
            options.RequiredLength = 8;
        });

        services.AddSingleton<IAuthSettings, AuthSettings>();
        services.AddSingleton<IRecoverySettings, RecoverySettings>();
        services.AddSingleton<IJwtSettings, JwtSettings>();
        services.AddSingleton<ISmtpSettings, SmtpSettings>();
        services.AddSingleton<ISmsNadoClientSettings, SmsNadoClientSettings>();
        services.AddSingleton<IProjectSettings, ProjectSettings>();
        services.AddSingleton<IUserSettings, UserSettings>();
        services.AddSingleton<IUserValidationSettings, UserValidationSettings>();
        services.AddSingleton<IFsStorageSettings, FsStorageSettings>();
        services.AddSingleton<IAuthContext, AuthContext>();
        services.AddSingleton<IFileStorage, FileSystemStorage>();
        services.AddSingleton<IOneTimePass, OneTimePass>();
        services.AddSingleton<IEmailClient, EmailClient>();
        services.AddSingleton<IInvitationSettings, InvitationSettings>();

        services.AddScoped<IBaseAuth, BaseAuth>();
        services.AddScoped<IPasswordHasher, PasswordHasher>();
        services.AddScoped<IVerificationTokens, VerificationTokens>();
        services.AddScoped<IMessageTemplates, MessageTemplates>();
        services.AddScoped<IOtpAuthFactor, OtpAuthFactor>();
        services.AddScoped<IAuthTokens, AuthTokens>();
        services.AddScoped<IPasswordRecoveryCodes, PasswordRecoveryCodes>();
        services.AddScoped<IPasswordRecovery, PasswordRecovery>();
        services.AddScoped<IInvitations, Invitations>();
        services.AddScoped<IUsers, Users>();
        services.AddScoped<IUserEmailChallenge, UserEmailChallenge>();
        services.AddScoped<IUserPhoneChallenge, UserPhoneChallenge>();
        services.AddScoped<ITenants, Tenants>();

        services.AddHttpClient<ICellularClient, SmsNadoClient>((provider, client) =>
            {
                var settings = provider.GetRequiredService<ISmsNadoClientSettings>();

                client.BaseAddress = settings.BaseUrl;
            })
            .AddPolicyHandler((_, _) => HttpPolicyExtensions
                .HandleTransientHttpError()
                .Or<TimeoutRejectedException>()
                .WaitAndRetryAsync(
                    retryCount: 3,
                    sleepDurationProvider: i => TimeSpan.FromMilliseconds(100 * Math.Pow(2, i)))
            )
            .AddPolicyHandler((_, _) => HttpPolicyExtensions
                .HandleTransientHttpError()
                .Or<TimeoutRejectedException>()
                .OrResult(r => r.StatusCode == (HttpStatusCode)429) // Too Many Requests
                .CircuitBreakerAsync(
                    handledEventsAllowedBeforeBreaking: 5,
                    durationOfBreak: TimeSpan.FromSeconds(15)
                ));

        services.AddHttpClient<IProjects, Projects>((provider, client) =>
            {
                var settings = provider.GetRequiredService<IProjectSettings>();

                client.BaseAddress = settings.BaseUrl;
                client.DefaultRequestHeaders.Authorization =
                    new AuthenticationHeaderValue("Bearer", settings.AccessToken);
            })
            .AddPolicyHandler((_, _) => HttpPolicyExtensions
                .HandleTransientHttpError()
                .Or<TimeoutRejectedException>()
                .WaitAndRetryAsync(
                    retryCount: 3,
                    sleepDurationProvider: i => TimeSpan.FromMilliseconds(100 * Math.Pow(2, i)))
            )
            .AddPolicyHandler((_, _) => HttpPolicyExtensions
                .HandleTransientHttpError()
                .Or<TimeoutRejectedException>()
                .OrResult(r => r.StatusCode == (HttpStatusCode)429) // Too Many Requests
                .CircuitBreakerAsync(
                    handledEventsAllowedBeforeBreaking: 5,
                    durationOfBreak: TimeSpan.FromSeconds(15)
                ));

        return services;
    }
}
