using System.Security.Claims;

namespace Domain.Auth.Tokens.Claims;

public class TenantClaim : Claim
{
    private const string Name = "tenant";

    public TenantClaim(string tenantId) : base(Name, tenantId)
    {
    }
}
