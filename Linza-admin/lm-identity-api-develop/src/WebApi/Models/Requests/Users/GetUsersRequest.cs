using Domain.Search;
using Domain.Users;
using System.ComponentModel.DataAnnotations;

namespace WebApi.Models.Requests.Users;

public class GetUsersRequest
{
    public string? SearchTerm { get; set; }

    public string[] IncludeIds { get; set; } = Array.Empty<string>();

    public string[] ExcludeIds { get; set; } = Array.Empty<string>();

    public string? TenantId { get; set; }

    [Range(1, int.MaxValue / 100)]
    public int? PageNumber { get; set; } = 1;

    [Range(1, 100)]
    public int? PageSize { get; set; } = 100;

    public IUserSearchQuery SearchQuery(IUsers users)
    {
        IUserSearchQuery query = users.Search().WithPagination(
            new Pagination(PageNumber ?? 1, PageSize ?? 100
            ));

        if (!string.IsNullOrEmpty(SearchTerm))
        {
            query = query.WithSearchTerm(SearchTerm);
        }

        if (IncludeIds.Any())
        {
            query = query.WithIds(IncludeIds);
        }

        if (ExcludeIds.Any())
        {
            query = query.WithoutIds(ExcludeIds);
        }

        if (!string.IsNullOrEmpty(TenantId))
        {
            query = query.WithTenant(TenantId);
        }

        return query;
    }
}
