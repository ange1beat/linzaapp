using Asp.Versioning.ApiExplorer;
using Microsoft.OpenApi.Models;

namespace WebApi.Extensions.Swagger;

public static class SwaggerExtension
{
    public static IServiceCollection AddSwagger(
        this IServiceCollection services)
    {
        services.AddSwaggerGen(options =>
        {
            var versionProvider = services.BuildServiceProvider()
                .GetRequiredService<IApiVersionDescriptionProvider>();

            foreach (var description in versionProvider.ApiVersionDescriptions)
            {
                var version = description.ApiVersion.ToString();
                var info = new OpenApiInfo
                {
                    Title = $"Linza Monitoring - Project API v{version}",
                    Version = version
                };

                if (description.IsDeprecated)
                {
                    info.Description +=
                        " This API version has been deprecated." +
                        " Please use one of the new APIs available from the explorer.";
                }

                options.SwaggerDoc(description.GroupName, info);
            }

            options.OperationFilter<AppResponsesOperationFilter>();

            options.AddSecurityDefinition(
                "bearer",
                new OpenApiSecurityScheme { Type = SecuritySchemeType.Http, Scheme = "bearer" }
            );

            options.AddSecurityRequirement(new OpenApiSecurityRequirement
            {
                {
                    new OpenApiSecurityScheme
                    {
                        Reference = new OpenApiReference
                        {
                            Type = ReferenceType.SecurityScheme, Id = "bearer"
                        }
                    },
                    new List<string>()
                }
            });

            options.UseDateOnlyTimeOnlyStringConverters();
        });

        return services;
    }
}
