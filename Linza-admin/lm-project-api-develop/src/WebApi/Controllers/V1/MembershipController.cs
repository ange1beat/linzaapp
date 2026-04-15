using Asp.Versioning;
using Domain.Authentication;
using Domain.Projects.Exceptions;
using Domain.Projects.Membership;
using Domain.Users;
using Domain.Users.Exceptions;
using Microsoft.AspNetCore.Mvc;
using WebApi.Models.Requests;
using WebApi.Models.Responses;

namespace WebApi.Controllers.V1;

[ApiVersion("1.0")]
[Route("v{version:apiVersion}/projects/membership")]
public class MembershipController : ApiControllerBase
{
    private readonly IProjectsMembership _membership;
    private readonly IUsers _users;

    public MembershipController(IProjectsMembership membership, IUsers users)
    {
        _membership = membership;
        _users = users;
    }

    [HttpGet("me")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    public async Task<ActionResult<MembershipResponse>> GetMembership()
    {
        IUserIdentity requester = UserIdentity();

        IEnumerable<string> projectIds = await _membership.ProjectIds(requester);

        return Ok(new MembershipResponse(requester.UserId, projectIds));
    }

    [HttpGet("{userId}")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    public async Task<ActionResult<MembershipResponse>> GetMembership(
        [FromRoute] string userId)
    {
        IUserIdentity requester = UserIdentity();

        if (userId == requester.UserId)
        {
            return await GetMembership();
        }

        try
        {
            IUser user = await _users.User(userId, requester);
            IEnumerable<string> projectIds = await _membership.ProjectIds(user, requester);

            return Ok(new MembershipResponse(userId, projectIds));
        }
        catch (UserNotFoundException exc)
        {
            return NotFound(exc.Message);
        }
    }

    [HttpPatch("{userId}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType<ValidationProblemDetails>(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> PatchMembership(
        [FromRoute] string userId,
        [FromBody] PatchMembershipRequest request)
    {
        try
        {
            IUserIdentity requester = UserIdentity();

            IUser user = await _users.User(userId, requester);

            await request.ApplyPatch(_membership, user, requester);

            return NoContent();
        }
        catch (UserNotFoundException exc)
        {
            return NotFound(exc.Message);
        }
        catch (ProjectsNotFoundException exc)
        {
            ModelState.AddModelError(nameof(request.ProjectIds), exc.Message);

            return BadRequest(ModelState);
        }
    }
}
