using Microsoft.IdentityModel.JsonWebTokens;
using System.Security.Claims;

namespace Domain.Auth.Tokens.Claims;

public class IdClaim : Claim
{
    public IdClaim(string userId) : base(JwtRegisteredClaimNames.Sub, userId)
    {
    }
}
