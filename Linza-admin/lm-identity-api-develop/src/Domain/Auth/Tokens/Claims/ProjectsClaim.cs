using Microsoft.IdentityModel.JsonWebTokens;
using System.Security.Claims;
using System.Text.Json;

namespace Domain.Auth.Tokens.Claims;

public class ProjectsClaim : Claim
{
    private const string Name = "projects";

    public ProjectsClaim(IEnumerable<string> projectIds) : base(
        Name, JsonSerializer.Serialize(projectIds), JsonClaimValueTypes.JsonArray)
    {
    }
}
