using Asp.Versioning;
using Domain.Projects.Exceptions;
using Domain.Projects.Favorites;
using Microsoft.AspNetCore.Mvc;
using System.Net.Mime;
using WebApi.Models.Authentication.Guards;
using WebApi.Models.Responses;

namespace WebApi.Controllers.V1;

[ApiVersion("1.0")]
[Route("v{version:apiVersion}/projects/favorites")]
public class FavoritesController : ApiControllerBase
{
    private readonly IFavoriteProjects _favorites;
    private readonly IResourceGuard _guard;

    public FavoritesController(
        IFavoriteProjects favorites,
        IResourceGuard guard)
    {
        _favorites = favorites;
        _guard = guard;
    }

    [HttpGet("")]
    [Produces(MediaTypeNames.Application.Json)]
    [ProducesResponseType(StatusCodes.Status200OK)]
    public async Task<ActionResult<FavoritesResponse>> GetFavorites()
    {
        IEnumerable<IFavoriteProjectInfo> favorites = await _favorites.All(UserIdentity());

        return Ok(new FavoritesResponse(favorites, _guard));
    }

    [HttpPut("{projectId}")]
    [Produces(MediaTypeNames.Application.Json)]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType<ConflictResponse>(StatusCodes.Status409Conflict)]
    public async Task<IActionResult> AddToFavorites([FromRoute] string projectId)
    {
        try
        {
            await _favorites.Put(projectId, UserIdentity());

            return NoContent();
        }
        catch (ProjectNotFoundException exc)
        {
            return NotFound(exc.Message);
        }
        catch (SizeLimitExceededException exc)
        {
            return Conflict(new FavoriteMaxSizeConflictResponse(exc.MaxSize));
        }
    }

    [HttpDelete("{projectId}")]
    [Produces(MediaTypeNames.Application.Json)]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    public async Task<IActionResult> RemoveFromFavorites([FromRoute] string projectId)
    {
        await _favorites.Remove(projectId, UserIdentity());

        return NoContent();
    }
}
