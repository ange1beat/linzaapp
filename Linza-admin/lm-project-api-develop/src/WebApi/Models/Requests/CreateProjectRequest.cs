using Domain.Authentication;
using Domain.Projects;
using Domain.Users;
using System.ComponentModel.DataAnnotations;
using WebApi.Attributes;

namespace WebApi.Models.Requests;

public class CreateProjectRequest
{
    [Required]
    [ProjectName]
    public string Name { get; set; } = null!;

    public IEnumerable<string> MemberIds { get; set; } = new List<string>();

    public async Task<IProject> NewProject(
        IProjects projects,
        IUsers users,
        IUserIdentity requester)
    {
        IEnumerable<IUser> members = await users.AllUsers(MemberIds, requester);

        return await projects.NewProject(
            new NewProjectData(Name, members),
            requester
        );
    }
}
