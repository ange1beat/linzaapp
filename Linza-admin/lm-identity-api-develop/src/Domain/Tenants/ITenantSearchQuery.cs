using Domain.Search;

namespace Domain.Tenants;

public interface ITenantSearchQuery
{
    ITenantSearchQuery WithTerm(string searchTerm);

    ITenantSearchQuery WithPagination(Pagination pagination);

    Task<IReadOnlyCollection<ITenant>> Result();

    Task<int> Total();
}
