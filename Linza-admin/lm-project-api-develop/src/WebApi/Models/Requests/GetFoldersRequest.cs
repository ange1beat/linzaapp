using System.ComponentModel.DataAnnotations;
using Domain.Projects.Folders;
using Domain.Search;

namespace WebApi.Models.Requests;

public class GetFoldersRequest
{
    public string Name { get; set; } = "";

    [Range(1, int.MaxValue)]
    public int PageNumber { get; set; } = 1;

    [Range(1, 100)]
    public int PageSize { get; set; } = 100;

    public IFolderSearchQuery SearchQuery(IProjectFolders projectFolders)
    {
        IFolderSearchQuery query = projectFolders.SearchQuery()
            .WithPagination(new Pagination(PageNumber, PageSize));

        if (!string.IsNullOrEmpty(Name))
        {
            query = query.WithName(Name);
        }

        return query;
    }
}
