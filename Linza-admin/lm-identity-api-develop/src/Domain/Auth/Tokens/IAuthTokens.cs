namespace Domain.Auth.Tokens;

public interface IAuthTokens
{
    Task<AuthToken> NewToken(string stateToken);

    Task<AuthToken> RefreshedToken(string refreshToken);

    Task RevokeRefreshToken(string refreshToken);
}
