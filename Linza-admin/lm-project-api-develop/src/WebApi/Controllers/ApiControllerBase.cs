using System.Net.Mime;
using Domain.Authentication;
using Microsoft.AspNetCore.Mvc;
using WebApi.Models.Authentication.Users;

namespace WebApi.Controllers;

[ApiController]
[Produces(MediaTypeNames.Application.Json)]
[ProducesResponseType(StatusCodes.Status401Unauthorized)]
[ProducesResponseType(StatusCodes.Status403Forbidden)]
[ProducesResponseType(StatusCodes.Status500InternalServerError)]
public abstract class ApiControllerBase : ControllerBase
{
    protected IUserIdentity UserIdentity() => new ClaimsUserIdentity(base.User);
}
