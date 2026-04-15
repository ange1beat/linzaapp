using System.Security.Claims;

namespace WebApi.Models.Authentication;

public class UserClaimTypes
{
    public const string Id = ClaimTypes.NameIdentifier;
    public const string Tenant = "tenant";
    public const string AccessToken = "access_token";
    public const string Roles = "roles";
}
