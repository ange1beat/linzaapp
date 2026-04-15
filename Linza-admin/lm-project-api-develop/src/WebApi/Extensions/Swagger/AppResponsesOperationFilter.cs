using Microsoft.OpenApi.Models;
using Swashbuckle.AspNetCore.SwaggerGen;

namespace WebApi.Extensions.Swagger;

public sealed class AppResponsesOperationFilter : IOperationFilter
{
    public void Apply(OpenApiOperation operation, OperationFilterContext context)
    {
        AddCommonResponses(operation, context);
    }

    private static void AddCommonResponses(
        OpenApiOperation operation,
        OperationFilterContext context)
    {
        if (operation.Responses.All(r => r.Key != "500"))
        {
            operation.Responses.Add("500", new OpenApiResponse
            {
                Description = "Internal Server Error"
            });
        }
    }
}
