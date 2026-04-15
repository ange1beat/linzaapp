using System.ComponentModel.DataAnnotations;
using Domain.Authentication;
using Domain.Projects;
using Domain.Search;

namespace WebApi.Models.Requests;

public class GetProjectsRequest
{
    public string Name { get; set; } = "";

    [Range(1, int.MaxValue)]
    public int PageNumber { get; set; } = 1;

    [Range(1, int.MaxValue)]
    public int PageSize { get; set; } = int.MaxValue;

    public IProjectSearchQuery SearchQuery(IProjects projects, IUserIdentity user)
    {
        IProjectSearchQuery query = projects.Search(user)
            .WithPagination(new Pagination(PageNumber, PageSize));

        if (!string.IsNullOrEmpty(Name))
        {
            query = query.WithName(Name);
        }

        return query;
    }
}
