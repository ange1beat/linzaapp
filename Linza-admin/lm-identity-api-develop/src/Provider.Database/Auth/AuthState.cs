using Domain.Auth;
using Domain.Media;
using Provider.Database.Tokens;

namespace Provider.Database.Auth;

internal sealed class AuthState : IAuthState
{
    private readonly DbUserToken _stateToken;

    public AuthState(DbUserToken stateToken)
    {
        _stateToken = stateToken;
    }

    public void Write(IMedia media)
    {
        media.Write("User", new UserAuthInfo(_stateToken.User));
        media.Write("StateToken", _stateToken.Id);
        media.Write("ExpiresAt", _stateToken.ExpiresAt);
    }
}
