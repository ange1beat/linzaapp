using Microsoft.IdentityModel.Tokens;

namespace Domain.Auth;

public interface IJwtSettings
{
    string Issuer { get; }

    string Audience { get; }

    TimeSpan ExpirationTime { get; }

    IEnumerable<SecurityKey> SigningKeys();

    SigningCredentials SigningCredentials();
}
