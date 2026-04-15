using Domain.Auth.Identity;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text.Json;

namespace Domain.Auth.Tokens.Claims;

public class RolesClaim : Claim
{
    private const string Name = "roles";

    public RolesClaim(IEnumerable<Role> userRoles) : base(
        Name, SerializedRoles(userRoles), JsonClaimValueTypes.JsonArray)
    {
    }

    private static string SerializedRoles(IEnumerable<Role> userRoles)
    {
        return JsonSerializer.Serialize(userRoles.Select(r => r.ToString()));
    }
}
