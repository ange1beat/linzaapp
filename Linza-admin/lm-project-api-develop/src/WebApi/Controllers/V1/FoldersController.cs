using Asp.Versioning;
using Domain.Projects;
using Domain.Projects.Exceptions;
using Domain.Projects.Folders;
using Microsoft.AspNetCore.Mvc;
using WebApi.Models.Requests;
using WebApi.Models.Responses;

namespace WebApi.Controllers.V1;

[ApiVersion("1.0")]
[Route("v{version:apiVersion}/projects/{projectId}/folders")]
[ProducesResponseType(StatusCodes.Status404NotFound)]
public class FoldersController : ApiControllerBase
{
    private readonly IProjects _projects;

    public FoldersController(IProjects projects)
    {
        _projects = projects;
    }

    [HttpPost("")]
    [ProducesResponseType(StatusCodes.Status201Created)]
    [ProducesResponseType<ValidationProblemDetails>(StatusCodes.Status400BadRequest)]
    [ProducesResponseType<ConflictResponse>(StatusCodes.Status409Conflict)]
    public async Task<ActionResult<FolderResponse>> CreateFolder(
        [FromRoute] string projectId,
        [FromBody] CreateFolderRequest request)
    {
        try
        {
            IProject project = await _projects.Project(projectId, UserIdentity());
            IFolder newFolder = await request.NewFolder(project);

            var response = new FolderResponse();
            newFolder.Write(response);

            return CreatedAtAction(
                nameof(GetFolder),
                new { projectId, folderId = response.Id },
                response
            );
        }
        catch (ProjectNotFoundException exc)
        {
            return NotFound(exc.Message);
        }
        catch (FolderNameConflictException)
        {
            return Conflict(new FolderNameConflictResponse());
        }
    }

    [HttpGet("")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType<ValidationProblemDetails>(StatusCodes.Status400BadRequest)]
    [ProducesResponseType<ConflictResponse>(StatusCodes.Status409Conflict)]
    public async Task<ActionResult<FolderPagedListResponse>> GetFolders(
        [FromRoute] string projectId,
        [FromQuery] GetFoldersRequest request)
    {
        try
        {
            IProject project = await _projects.Project(projectId, UserIdentity());

            IFolderSearchQuery foldersQuery = request.SearchQuery(project.Folders());

            return Ok(new FolderPagedListResponse(
                await foldersQuery.Result(),
                await foldersQuery.Total()
            ));
        }
        catch (ProjectNotFoundException exc)
        {
            return NotFound(exc.Message);
        }
    }

    [HttpGet("{folderId}")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType<ValidationProblemDetails>(StatusCodes.Status400BadRequest)]
    [ProducesResponseType<ConflictResponse>(StatusCodes.Status409Conflict)]
    public async Task<ActionResult<FolderResponse>> GetFolder(
        [FromRoute] string projectId,
        [FromRoute] string folderId)
    {
        try
        {
            IProject project = await _projects.Project(projectId, UserIdentity());

            IFolder folder = await project.Folders().Folder(folderId);

            var response = new FolderResponse();
            folder.Write(response);

            return Ok(response);
        }
        catch (ProjectNotFoundException exc)
        {
            return NotFound(exc.Message);
        }
        catch (FolderNotFoundException exc)
        {
            return NotFound(exc.Message);
        }
    }

    [HttpPut("{folderId}/name")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType<ValidationProblemDetails>(StatusCodes.Status400BadRequest)]
    [ProducesResponseType<ConflictResponse>(StatusCodes.Status409Conflict)]
    public async Task<ActionResult<FolderResponse>> RenameFolder(
        [FromRoute] string projectId,
        [FromRoute] string folderId,
        [FromBody] RenameFolderRequest request)
    {
        try
        {
            IProject project = await _projects.Project(projectId, UserIdentity());
            IFolder folder = await project.Folders().Folder(folderId);

            await request.RenameFolder(folder);

            return NoContent();
        }
        catch (ProjectNotFoundException exc)
        {
            return NotFound(exc.Message);
        }
        catch (FolderNotFoundException exc)
        {
            return NotFound(exc.Message);
        }
    }

    [HttpDelete("{folderId}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType<ValidationProblemDetails>(StatusCodes.Status400BadRequest)]
    [ProducesResponseType<ConflictResponse>(StatusCodes.Status409Conflict)]
    public async Task<ActionResult<FolderResponse>> DeleteFolder(
        [FromRoute] string projectId,
        [FromRoute] string folderId)
    {
        try
        {
            IProject project = await _projects.Project(projectId, UserIdentity());

            await project.Folders().Remove(folderId);

            return NoContent();
        }
        catch (ProjectNotFoundException exc)
        {
            return NotFound(exc.Message);
        }
        catch (FolderNotFoundException exc)
        {
            return NotFound(exc.Message);
        }
    }
}
