using Domain.Auth.Tokens;

namespace WebApi.Models.Responses.Auth;

public class AccessTokenResponse
{
    public string TokenType => "Bearer";

    public string AccessToken => _token.AccessToken;

    public DateTime ExpiresAt => _token.AccessExpiresAt;

    private readonly AuthToken _token;

    public AccessTokenResponse(AuthToken token)
    {
        _token = token;
    }
}
