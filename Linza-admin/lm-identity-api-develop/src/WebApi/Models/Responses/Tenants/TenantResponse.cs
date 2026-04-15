using Domain.Media;

namespace WebApi.Models.Responses.Tenants;

public class TenantResponse : ReflectedMedia
{
    public string Id { get; set; } = null!;

    public string Name { get; set; } = null!;
}
