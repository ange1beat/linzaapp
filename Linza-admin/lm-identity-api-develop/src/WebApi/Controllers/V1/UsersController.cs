using Asp.Versioning;
using Domain.Auth.Exceptions;
using Domain.Auth.Identity;
using Domain.Users;
using Domain.Users.Challenges;
using Domain.Users.Exceptions;
using Domain.Users.Invitations;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Net.Http.Headers;
using WebApi.Controllers.Attributes;
using WebApi.Models.Requests.Users;
using WebApi.Models.Responses.Users;

namespace WebApi.Controllers.V1;

[ApiController]
[ApiVersion("1.0")]
[Route("v{version:apiVersion}/users")]
[ProducesResponseType(StatusCodes.Status500InternalServerError)]
public class UsersController : ControllerBase
{
    private readonly IUsers _users;
    private readonly IInvitations _invitations;
    private readonly IAuthContext _authContext;

    public UsersController(
        IUsers users,
        IInvitations invitations,
        IAuthContext authContext)
    {
        _users = users;
        _invitations = invitations;
        _authContext = authContext;
    }

    [HttpPost("invitations")]
    [Authorize(Roles = "Supervisor")]
    [ProducesResponseType(StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    [ProducesResponseType(StatusCodes.Status409Conflict)]
    public async Task<IActionResult> CreateInvitations(
        [FromBody] CreateInvitationRequest request)
    {
        try
        {
            IInvitation invitation = await request.NewInvitation(_invitations);

            return CreatedAtAction(
                nameof(GetInvitation),
                new { invitationId = invitation.Id },
                null
            );
        }
        catch (UnsupportedCultureException)
        {
            ModelState.AddModelError(
                nameof(request.Language),
                "Unsupported language"
            );

            return ValidationProblem(ModelState);
        }
        catch (EmailConflictException exc)
        {
            return Conflict(exc.Message);
        }
    }

    [HttpGet("invitations/{invitationId}")]
    [ProducesResponseType<InvitationResponse>(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetInvitation(
        [FromRoute] string invitationId)
    {
        try
        {
            IInvitation invitation = await _invitations.Invitation(invitationId);

            var response = new InvitationResponse();
            invitation.Write(response);

            return Ok(response);
        }
        catch (InvitationNotFoundException)
        {
            return NotFound();
        }
    }

    [HttpPost("registration")]
    [ProducesResponseType(StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    [ProducesResponseType(StatusCodes.Status409Conflict)]
    public async Task<IActionResult> RegisterUser(
        [FromBody] RegisterUserRequest request)
    {
        try
        {
            IUser user = await request.NewUser(_users);

            return CreatedAtAction(
                nameof(GetUser),
                new { userId = user.Id },
                null
            );
        }
        catch (InvitationNotFoundException)
        {
            return Forbid();
        }
        catch (EmailConflictException)
        {
            return Forbid();
        }
    }

    [HttpPost("search")]
    [Authorize(Roles = "Supervisor,Admin")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<UserPagedListResponse>> GetUsers(
        [FromBody] GetUsersRequest request)
    {
        IUserSearchQuery searchQuery = request.SearchQuery(_users);

        return Ok(new UserPagedListResponse(
            await searchQuery.Result(),
            await searchQuery.Total()
        ));
    }

    [HttpGet("{userId}")]
    [Authorize(Roles = "Supervisor,Admin")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<ActionResult<UserResponse>> GetUser(
        [FromRoute] string userId)
    {
        try
        {
            IUser user = await _users.User(userId);

            var response = new UserResponse();
            user.Write(response);

            return Ok(response);
        }
        catch (UserNotFoundException)
        {
            return NotFound();
        }
    }

    [HttpDelete("{userId}")]
    [Authorize(Roles = "Supervisor,Admin")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> DeleteUser(string userId)
    {
        await _users.Remove(userId);

        return NoContent();
    }

    [HttpPatch("{userId}/roles")]
    [Authorize(Roles = "Supervisor,Admin")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> ChangeUserRoles(
        [FromRoute] string userId,
        [FromBody] ChangeUserRolesRequest request)
    {
        try
        {
            IUser user = await _users.User(userId);

            await request.ChangeRoles(user);

            return NoContent();
        }
        catch (UserNotFoundException)
        {
            return NotFound();
        }
    }

    [HttpGet("me")]
    [Authorize]
    [ProducesResponseType<UserResponse>(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<IActionResult> GetMe()
    {
        IUserIdentity identity = _authContext.LoggedInIdentity();

        try
        {
            IUser user = await _users.User(identity.UserId);

            var response = new UserResponse();
            user.Write(response);

            return Ok(response);
        }
        catch (UserNotFoundException)
        {
            return NotFound();
        }
    }

    [HttpPut("me/name")]
    [Authorize]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<IActionResult> RenameMe(
        [FromBody] RenameUserRequest request)
    {
        IUserIdentity identity = _authContext.LoggedInIdentity();

        try
        {
            IUser user = await _users.User(identity.UserId);

            await request.RenameUser(user);

            return NoContent();
        }
        catch (UserNotFoundException)
        {
            return NotFound();
        }
    }

    [HttpPost("me/email/change-request")]
    [Authorize]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status409Conflict)]
    [ProducesResponseType(StatusCodes.Status429TooManyRequests)]
    public async Task<IActionResult> RequestEmailChange(
        [FromBody] EmailChangeRequest request,
        [FromServices] IUserEmailChallenge challenge)
    {
        try
        {
            await request.Challenge(_users, challenge);

            return NoContent();
        }
        catch (UnsupportedCultureException)
        {
            ModelState.AddModelError(
                nameof(request.Language),
                "Unsupported language"
            );

            return ValidationProblem(ModelState);
        }
        catch (EmailConflictException exc)
        {
            return Conflict(exc.Message);
        }
        catch (RetryLimitExceededException exc)
        {
            Response.Headers.RetryAfter =
                HeaderUtilities.FormatDate(exc.RetryAfter);

            return new StatusCodeResult(429);
        }
    }

    [HttpPut("me/email")]
    [Authorize]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<IActionResult> ChangeMyEmail(
        [FromBody] ChangeMyEmailRequest request,
        [FromServices] IUserEmailChallenge challenge)
    {
        IUserIdentity identity = _authContext.LoggedInIdentity();

        try
        {
            IUser user = await _users.User(identity.UserId);

            await request.ChangeEmail(user, challenge);

            return NoContent();
        }
        catch (UserNotFoundException)
        {
            return NotFound();
        }
    }

    [HttpPost("me/phone/change-request")]
    [Authorize]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status409Conflict)]
    [ProducesResponseType(StatusCodes.Status429TooManyRequests)]
    public async Task<IActionResult> RequestPhoneChange(
        [FromBody] PhoneChangeRequest request,
        [FromServices] IUserPhoneChallenge challenge)
    {
        try
        {
            await request.Challenge(_users, challenge);

            return NoContent();
        }
        catch (UnsupportedCultureException)
        {
            ModelState.AddModelError(
                nameof(request.Language),
                "Unsupported language"
            );

            return ValidationProblem(ModelState);
        }
        catch (EmailConflictException exc)
        {
            return Conflict(exc.Message);
        }
        catch (RetryLimitExceededException exc)
        {
            Response.Headers.RetryAfter =
                HeaderUtilities.FormatDate(exc.RetryAfter);

            return new StatusCodeResult(429);
        }
    }

    [HttpPut("me/phone")]
    [Authorize]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<IActionResult> ChangeMyPhoneNumber(
        [FromBody] ChangeMyPhoneRequest request,
        [FromServices] IUserPhoneChallenge challenge)
    {
        IUserIdentity identity = _authContext.LoggedInIdentity();

        try
        {
            IUser user = await _users.User(identity.UserId);

            await request.ChangePhone(user, challenge);

            return NoContent();
        }
        catch (UserNotFoundException)
        {
            return NotFound();
        }
    }

    [HttpPut("me/telegram")]
    [Authorize]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<IActionResult> ChangeMyTelegram(
        [FromBody] ChangeMyTelegramRequest request)
    {
        IUserIdentity identity = _authContext.LoggedInIdentity();

        try
        {
            IUser user = await _users.User(identity.UserId);

            await request.ChangeTelegram(user);

            return NoContent();
        }
        catch (UserNotFoundException)
        {
            return NotFound();
        }
    }

    [HttpPut("me/avatar")]
    [Authorize]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType<string>(StatusCodes.Status404NotFound)]
    public async Task<ActionResult> ChangeMyAvatar([UserAvatar] IFormFile file)
    {
        IUserIdentity identity = _authContext.LoggedInIdentity();

        try
        {
            IUser user = await _users.User(identity.UserId);

            await user.AttachAvatar(
                file.OpenReadStream(),
                Path.GetExtension(file.FileName)
            );

            return NoContent();
        }
        catch (UserNotFoundException)
        {
            return NotFound();
        }
    }

    [HttpDelete("me/avatar")]
    [Authorize]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult> RemoveMyAvatar()
    {
        IUserIdentity identity = _authContext.LoggedInIdentity();

        try
        {
            IUser user = await _users.User(identity.UserId);

            await user.RemoveAvatar();

            return NoContent();
        }
        catch (UserNotFoundException)
        {
            return NotFound();
        }
    }

    [HttpPut("me/password")]
    [Authorize]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    public async Task<IActionResult> ChangeMyPassword(
        [FromBody] ChangeMyPasswordRequest request)
    {
        IUserIdentity identity = _authContext.LoggedInIdentity();

        try
        {
            IUser user = await _users.User(identity.UserId);

            await request.ChangePassword(user);

            return NoContent();
        }
        catch (UserNotFoundException)
        {
            return NotFound();
        }
    }
}
