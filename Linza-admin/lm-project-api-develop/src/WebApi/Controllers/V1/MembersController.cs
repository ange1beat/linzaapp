using Asp.Versioning;
using Domain.Authentication;
using Domain.Projects;
using Domain.Projects.Exceptions;
using Domain.Users;
using Domain.Users.Exceptions;
using Microsoft.AspNetCore.Mvc;
using WebApi.Models.Requests;
using WebApi.Models.Responses;

namespace WebApi.Controllers.V1;

[ApiVersion("1.0")]
[Route("v{version:apiVersion}/projects/{projectId}/members")]
[ProducesResponseType(StatusCodes.Status404NotFound)]
public class MembersController : ApiControllerBase
{
    private readonly IProjects _projects;
    private readonly IUsers _users;

    public MembersController(IProjects projects, IUsers users)
    {
        _projects = projects;
        _users = users;
    }

    [HttpGet("")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    public async Task<ActionResult<ProjectMembersResponse>> GetProjectMembers(
        [FromRoute] string projectId)
    {
        try
        {
            IUserIdentity requester = UserIdentity();

            IProject project = await _projects.Project(projectId, requester);
            IEnumerable<IUser> supervisors = await _users.Supervisors(requester);

            return Ok(new ProjectMembersResponse(
                new List<string>(project.Members())
                    .Union(supervisors.Select(s => s.Id))
            ));
        }
        catch (ProjectNotFoundException exc)
        {
            return NotFound(exc.Message);
        }
    }

    [HttpPost("")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType<ValidationProblemDetails>(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> AddProjectMembers(
        [FromRoute] string projectId,
        AddProjectMembersRequest request)
    {
        try
        {
            IUserIdentity requester = UserIdentity();

            IProject project = await _projects.Project(projectId, requester);
            IEnumerable<IUser> users = await _users.AllUsers(request.UserIds, requester);

            await project.Members().Add(users);

            return NoContent();
        }
        catch (ProjectNotFoundException exc)
        {
            return NotFound(exc.Message);
        }
        catch (UsersNotFoundException exc)
        {
            ModelState.AddModelError(nameof(request.UserIds), exc.Message);

            return BadRequest(ModelState);
        }
    }

    [HttpDelete("{userId}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    public async Task<IActionResult> RemoveProjectMember(
        [FromRoute] string projectId,
        [FromRoute] string userId)
    {
        try
        {
            IProject project = await _projects.Project(projectId, UserIdentity());

            await project.Members().Remove(userId);

            return NoContent();
        }
        catch (ProjectNotFoundException exc)
        {
            return NotFound(exc.Message);
        }
    }
}
