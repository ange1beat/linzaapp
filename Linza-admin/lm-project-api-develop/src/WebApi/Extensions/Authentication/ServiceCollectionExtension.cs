using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using System.Security.Claims;
using System.Security.Cryptography;
using WebApi.Models.Authentication;

namespace WebApi.Extensions.Authentication;

public static class ServiceCollectionExtension
{
    public static IServiceCollection AddJwtBearerAuthentication(
        this IServiceCollection services,
        IConfiguration config)
    {
        var settings = new JwtSettings(config);
        var rsaKey = RSA.Create();

        rsaKey.ImportFromPem(settings.PublicKey);

        services
            .AddAuthentication(options =>
            {
                options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
                options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
                options.DefaultScheme = JwtBearerDefaults.AuthenticationScheme;
            })
            .AddJwtBearer(options =>
            {
                options.TokenValidationParameters = new TokenValidationParameters
                {
                    ValidateIssuer = true,
                    ValidateAudience = true,
                    ValidateLifetime = true,
                    ValidateIssuerSigningKey = true,
                    ClockSkew = TimeSpan.Zero,
                    ValidIssuer = settings.Issuer,
                    ValidAudience = settings.Audience,
                    IssuerSigningKey = new RsaSecurityKey(rsaKey.ExportParameters(false)),
                };

                options.Events = new JwtBearerEvents
                {
                    OnTokenValidated = context =>
                    {
                        AddAccessTokenClaim(context);

                        return Task.CompletedTask;
                    }
                };
            });

        return services;
    }

    // Add the access token as a claim to the ClaimsPrincipal
    private static void AddAccessTokenClaim(TokenValidatedContext context)
    {
        var claimsIdentity = context.Principal?.Identity as ClaimsIdentity;
        claimsIdentity?.AddClaim(new Claim(
            UserClaimTypes.AccessToken,
            context.SecurityToken.UnsafeToString()
        ));
    }
}
