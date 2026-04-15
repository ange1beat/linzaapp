using System.Security.Claims;

namespace WebApi.Models.Auth;

public class LinzaClaimTypes
{
    public const string UserId = ClaimTypes.NameIdentifier; //In JWT this is "sub" claim.
    public const string TenantId = "tenant";
    public const string Roles = "roles";
}
