using Asp.Versioning;
using Asp.Versioning.ApiExplorer;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.OpenApi.Models;
using Newtonsoft.Json.Converters;
using Newtonsoft.Json.Serialization;
using System.Text.Json.Serialization;
using WebApi.Controllers.Filters;
using WebApi.Extensions.Application;
using WebApi.Extensions.Authentication;
using WebApi.Extensions.Database;
using WebApi.Extensions.Environments;
using WebApi.Extensions.Swagger;

var builder = WebApplication.CreateBuilder(args);
{
    builder.Services
        .AddDatabase(builder.Configuration)
        .AddApplicationServices(builder.Configuration);

    builder.Services
        .AddEndpointsApiExplorer()
        .AddSwagger()
        .AddHttpContextAccessor()
        .AddControllers(options =>
            options.Filters.Add<ExceptionFilter>()
        )
        .AddJsonOptions(options =>
        {
            options.JsonSerializerOptions.Converters
                .Add(new JsonStringEnumConverter());
        })
        .AddNewtonsoftJson(options =>
        {
            options.SerializerSettings.ContractResolver =
                new CamelCasePropertyNamesContractResolver();

            options.SerializerSettings.Converters
                .Add(new StringEnumConverter());
        });

    builder.Services.Configure<ApiBehaviorOptions>(options =>
    {
        options.SuppressMapClientErrors = true;
    });

    builder.Services
        .AddApiVersioning(options =>
        {
            options.AssumeDefaultVersionWhenUnspecified = false;
            options.ReportApiVersions = true;
            options.ApiVersionReader = new UrlSegmentApiVersionReader();
        })
        .AddApiExplorer(options =>
        {
            options.GroupNameFormat = "'v'VVV";
            options.SubstituteApiVersionInUrl = true;
        });

    builder.Services.AddJwtBearerAuthentication(builder.Configuration);
    builder.Services.AddAuthorization(options =>
    {
        options.DefaultPolicy = new AuthorizationPolicyBuilder()
            .RequireAuthenticatedUser()
            .Build();
    });
}

var app = builder.Build();
{
    app
        .UseRouting()
        .UseAuthentication()
        .UseAuthorization()
        .UseEndpoints(endpoints => endpoints
            .MapControllers()
            .RequireAuthorization()
        );

    if (app.Environment.IsLocal() || app.Environment.IsDevelopment())
    {
        app.UseSwagger(config =>
        {
            config.PreSerializeFilters.Add((document, request) =>
            {
                if (request.Headers.TryGetValue("X-Forwarded-Path", out var header))
                {
                    document.Servers = new List<OpenApiServer> { new() { Url = $"{header}" } };
                }
            });
        });

        var versionProvider = app.Services.GetRequiredService<IApiVersionDescriptionProvider>();

        app.UseSwaggerUI(options =>
        {
            foreach (var description in versionProvider.ApiVersionDescriptions)
            {
                options.SwaggerEndpoint(
                    $"/swagger/{description.GroupName}/swagger.json",
                    description.GroupName
                );
            }
        });
    }
}

app.MigrateDatabase();

app.Run();
