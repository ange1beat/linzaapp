using Asp.Versioning;
using Domain.Auth.Identity;
using Domain.Tenants;
using Domain.Users;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using WebApi.Models.Requests.Tenants;
using WebApi.Models.Responses.Tenants;

namespace WebApi.Controllers.V1;

[ApiController]
[ApiVersion("1.0")]
[Produces("application/json")]
[Consumes("application/json")]
[Route("v{version:apiVersion}/tenants")]
[ProducesResponseType(StatusCodes.Status401Unauthorized)]
[ProducesResponseType(StatusCodes.Status500InternalServerError)]
public class TenantsController : ControllerBase
{
    private readonly ITenants _tenants;

    public TenantsController(ITenants tenants)
    {
        _tenants = tenants;
    }

    [HttpGet("")]
    [Authorize(Roles = "Admin")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<IActionResult> GetTenants(
        [FromQuery] GetTenantsRequest request)
    {
        ITenantSearchQuery query = request.SearchQuery(_tenants);

        return Ok(new TenantPagedListResponse(
            await query.Result(),
            await query.Total()
        ));
    }

    [HttpGet("{tenantId}")]
    [Authorize(Roles = "Supervisor,Admin")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetTenant([FromRoute] string tenantId)
    {
        try
        {
            ITenant tenant = await _tenants.Tenant(tenantId);

            var response = new TenantResponse();
            tenant.Write(response);

            return Ok(response);
        }
        catch (TenantNotFoundException)
        {
            return NotFound();
        }
    }

    [HttpGet("{tenantId}/users")]
    [Authorize(Roles = "Supervisor,Admin")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status403Forbidden)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<IActionResult> GetTenantUsers(
        [FromRoute] string tenantId,
        [FromServices] IUsers users)
    {
        IEnumerable<IUser> tenantUsers = await users.Search()
            .WithTenant(tenantId)
            .Result();

        return Ok(new TenantUsersResponse(tenantUsers));
    }

    [HttpGet("my")]
    [Authorize]
    [ProducesResponseType(StatusCodes.Status200OK)]
    public async Task<IActionResult> GetMyTenant(
        [FromServices] IAuthContext authCtx)
    {
        IUserIdentity identity = authCtx.LoggedInIdentity();

        ITenant tenant = await _tenants.Tenant(identity.TenantId);

        var response = new TenantResponse();
        tenant.Write(response);

        return Ok(response);
    }
}
