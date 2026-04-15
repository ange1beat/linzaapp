using Domain.Auth.Identity;
using System.Security.Claims;

namespace WebApi.Models.Auth;

public class ApiUserIdentity : IUserIdentity
{
    private const string AnonymousUserId = "anonymous";

    public string UserId => _httpContext.User.FindFirstValue(LinzaClaimTypes.UserId)
        ?? AnonymousUserId;

    public string TenantId => _httpContext.User.FindFirstValue(LinzaClaimTypes.TenantId)
        ?? string.Empty;

    private readonly HttpContext _httpContext;

    public ApiUserIdentity(HttpContext httpContext)
    {
        _httpContext = httpContext;
    }

    public bool IsInRole(Role role)
    {
        return _httpContext.User.IsInRole(role.ToString());
    }
}
