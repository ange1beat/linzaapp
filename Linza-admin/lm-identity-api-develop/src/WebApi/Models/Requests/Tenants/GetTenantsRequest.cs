using Domain.Search;
using Domain.Tenants;
using System.ComponentModel.DataAnnotations;

namespace WebApi.Models.Requests.Tenants;

public class GetTenantsRequest
{
    public string SearchTerm { get; set; } = string.Empty;

    [Range(1, int.MaxValue)]
    public int PageNumber { get; set; } = 1;

    [Range(1, int.MaxValue)]
    public int PageSize { get; set; } = 100;

    public ITenantSearchQuery SearchQuery(ITenants tenants)
    {
        return tenants.Search()
            .WithTerm(SearchTerm)
            .WithPagination(new Pagination(PageNumber, PageSize));
    }
}
