using Domain.Tenants;

namespace WebApi.Models.Responses.Tenants;

public class TenantPagedListResponse
{
    public IEnumerable<TenantResponse> Tenants => _tenants.Select(t =>
    {
        var response = new TenantResponse();
        t.Write(response);

        return response;
    });

    public int Total { get; }

    private readonly IEnumerable<ITenant> _tenants;

    public TenantPagedListResponse(IEnumerable<ITenant> tenants, int total)
    {
        _tenants = tenants;
        Total = total;
    }
}
