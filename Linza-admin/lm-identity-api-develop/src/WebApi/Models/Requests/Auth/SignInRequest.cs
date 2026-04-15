using Domain.Auth.Tokens;
using System.ComponentModel.DataAnnotations;

namespace WebApi.Models.Requests.Auth;

public class SignInRequest
{
    [Required(AllowEmptyStrings = false)]
    public string StateToken { get; set; } = string.Empty;

    public Task<AuthToken> NewToken(IAuthTokens tokens)
    {
        return tokens.NewToken(StateToken);
    }
}
