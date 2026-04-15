using Domain.Search;

namespace Domain.Projects;

public interface IProjectSearchQuery
{
    IProjectSearchQuery WithName(string name);

    IProjectSearchQuery WithIds(params string[] ids);

    IProjectSearchQuery WithTenant(string tenantId);

    IProjectSearchQuery WithPagination(Pagination pagination);

    Task<bool> Any();

    Task<IReadOnlyList<IProject>> Projects();

    Task<int> Total();
}
