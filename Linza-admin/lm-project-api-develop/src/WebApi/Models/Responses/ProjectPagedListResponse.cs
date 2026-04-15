using Domain.Projects;
using WebApi.Models.Authentication.Guards;

namespace WebApi.Models.Responses;

public class ProjectPagedListResponse
{
    public IEnumerable<ProjectResponse> Projects => _projects.Select(p =>
    {
        var dto = new ProjectResponse(_guard);
        p.Write(dto);

        return dto;
    });

    public int Total { get; set; }

    private readonly IEnumerable<IProject> _projects;
    private readonly IResourceGuard _guard;

    public ProjectPagedListResponse(
        IResourceGuard guard,
        IEnumerable<IProject> projects,
        int total)
    {
        _guard = guard;
        _projects = projects;

        Total = total;
    }
}
