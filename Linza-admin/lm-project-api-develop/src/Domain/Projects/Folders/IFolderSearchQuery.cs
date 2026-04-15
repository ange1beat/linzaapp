using Domain.Search;

namespace Domain.Projects.Folders;

public interface IFolderSearchQuery
{
    IFolderSearchQuery WithName(string name);

    IFolderSearchQuery WithPagination(Pagination pagination);

    Task<IReadOnlyCollection<IFolder>> Result();

    Task<int> Total();
}
