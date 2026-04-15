using Domain.Authentication;
using System.Security.Claims;

namespace WebApi.Models.Authentication.Users;

public class ClaimsUserIdentity : IUserIdentity
{
    private const string SupervisorRole = "Supervisor";
    private const string AdminRole = "Admin";

    public string UserId => _userId.Value;

    public string TenantId => _tenantId.Value;

    private readonly ClaimsPrincipal _principal;
    private readonly Lazy<string> _userId;
    private readonly Lazy<string> _tenantId;

    public ClaimsUserIdentity(ClaimsPrincipal principal) : this(
        principal, UserIdLazy(principal), TenantIdLazy(principal))
    {
    }

    private ClaimsUserIdentity(
        ClaimsPrincipal principal,
        Lazy<string> userId,
        Lazy<string> tenantId)
    {
        _principal = principal;
        _userId = userId;
        _tenantId = tenantId;
    }

    public string AccessToken() => MandatoryClaim(UserClaimTypes.AccessToken).Value;

    public bool IsAdmin() => _principal.IsInRole(AdminRole);

    public bool IsSupervisor() => _principal.IsInRole(SupervisorRole);

    private static Lazy<string> UserIdLazy(ClaimsPrincipal principal)
    {
        return new Lazy<string>(() =>
            MandatoryClaim(principal, UserClaimTypes.Id).Value
        );
    }

    private static Lazy<string> TenantIdLazy(ClaimsPrincipal principal)
    {
        return new Lazy<string>(() =>
            MandatoryClaim(principal, UserClaimTypes.Tenant).Value
        );
    }

    private static Claim MandatoryClaim(ClaimsPrincipal principal, string claimType)
    {
        Claim? claim = principal.FindFirst(c => c.Type.Equals(claimType));

        if (claim is null)
        {
            throw new UnauthorizedAccessException();
        }

        return claim;
    }

    private Claim MandatoryClaim(string claimType)
    {
        return MandatoryClaim(_principal, claimType);
    }
}
