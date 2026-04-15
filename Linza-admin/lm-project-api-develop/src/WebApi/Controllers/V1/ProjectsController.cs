using Asp.Versioning;
using Domain.Exceptions;
using Domain.Projects;
using Domain.Projects.Exceptions;
using Domain.Users;
using Domain.Users.Exceptions;
using Microsoft.AspNetCore.Mvc;
using WebApi.Attributes;
using WebApi.Models.Authentication.Guards;
using WebApi.Models.Requests;
using WebApi.Models.Responses;

namespace WebApi.Controllers.V1;

[ApiVersion("1.0")]
[Route("v{version:apiVersion}/projects")]
public class ProjectsController : ApiControllerBase
{
    private readonly IProjects _projects;
    private readonly IUsers _users;
    private readonly IResourceGuard _guard;

    public ProjectsController(IProjects projects, IUsers users, IResourceGuard guard)
    {
        _projects = projects;
        _users = users;
        _guard = guard;
    }

    [HttpPost]
    [ProducesResponseType(StatusCodes.Status201Created)]
    [ProducesResponseType<ValidationProblemDetails>(StatusCodes.Status400BadRequest)]
    [ProducesResponseType<ConflictResponse>(StatusCodes.Status409Conflict)]
    public async Task<ActionResult<ProjectResponse>> CreateProject(
        [FromBody] CreateProjectRequest request)
    {
        try
        {
            IProject project = await request.NewProject(_projects, _users, UserIdentity());

            var response = new ProjectResponse(_guard);
            project.Write(response);

            return CreatedAtAction(
                nameof(GetProject),
                new { projectId = response.Id },
                response
            );
        }
        catch (UsersNotFoundException exc)
        {
            ModelState.AddModelError(
                nameof(request.MemberIds),
                $"Unknown users: [{string.Join(',', exc.UserIds)}]"
            );

            return BadRequest(ModelState);
        }
        catch (ConstraintException)
        {
            return Conflict(new ProjectNameConflictResponse());
        }
    }

    [HttpGet]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType<ValidationProblemDetails>(StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<ProjectPagedListResponse>> GetProjects(
        [FromQuery] GetProjectsRequest request)
    {
        IProjectSearchQuery searchQuery = request.SearchQuery(_projects, UserIdentity());

        return Ok(
            new ProjectPagedListResponse(
                _guard,
                await searchQuery.Projects(),
                await searchQuery.Total()
            )
        );
    }

    [HttpGet("{projectId}")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<ActionResult<ProjectResponse>> GetProject(
        [FromRoute] string projectId)
    {
        try
        {
            IProject project = await _projects.Project(projectId, UserIdentity());

            var response = new ProjectResponse(_guard);
            project.Write(response);

            return Ok(response);
        }
        catch (ProjectNotFoundException exc)
        {
            return NotFound(exc.Message);
        }
    }

    [HttpDelete("{projectId}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    public async Task<ActionResult<ProjectResponse>> DeleteProject(
        [FromRoute] string projectId)
    {
        await _projects.Remove(projectId, UserIdentity());

        return NoContent();
    }

    [HttpPut("{projectId}/avatar")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType<ValidationProblemDetails>(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<ActionResult<ProjectResponse>> UploadProjectAvatar(
        [FromRoute] string projectId,
        [ProjectAvatar] IFormFile file)
    {
        try
        {
            IProject project = await _projects.Project(projectId, UserIdentity());

            await project.AttachAvatar(
                file.OpenReadStream(),
                Path.GetExtension(file.FileName)
            );

            return NoContent();
        }
        catch (ProjectNotFoundException exc)
        {
            return NotFound(exc.Message);
        }
    }

    [HttpDelete("{projectId}/avatar")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<ActionResult<ProjectResponse>> DeleteProjectAvatar(
        [FromRoute] string projectId)
    {
        try
        {
            IProject project = await _projects.Project(projectId, UserIdentity());

            await project.RemoveAvatar();

            return NoContent();
        }
        catch (ProjectNotFoundException exc)
        {
            return NotFound(exc.Message);
        }
    }

    [HttpPut("{projectId}/name")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType<ValidationProblemDetails>(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType<ConflictResponse>(StatusCodes.Status409Conflict)]
    public async Task<IActionResult> RenameProject(
        [FromRoute] string projectId,
        [FromBody] UpdateProjectNameRequest request)
    {
        try
        {
            IProject project = await _projects.Project(projectId, UserIdentity());

            await project.Rename(request.Name);

            return NoContent();
        }
        catch (ProjectNotFoundException exc)
        {
            return NotFound(exc.Message);
        }
        catch (ConstraintException)
        {
            return Conflict(new ProjectNameConflictResponse());
        }
    }
}
