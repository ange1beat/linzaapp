namespace WebApi.Models.Responses;

public class ProjectMembersResponse
{
    public IEnumerable<string> UserIds { get; }

    public ProjectMembersResponse(IEnumerable<string> userIds)
    {
        UserIds = userIds;
    }
}
