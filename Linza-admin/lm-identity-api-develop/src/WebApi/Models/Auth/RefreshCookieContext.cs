using Domain.Auth.Tokens;

namespace WebApi.Models.Auth;

public class RefreshCookieContext
{
    private const string Name = "lm_rt";

    private static readonly CookieOptions _defaultOptions = new()
    {
        Secure = true,
        HttpOnly = true,
        SameSite = SameSiteMode.Strict
    };

    public bool Contains(HttpRequest request)
    {
        return request.Cookies.ContainsKey(Name);
    }

    public string Value(HttpRequest request)
    {
        return request.Cookies[Name] ?? string.Empty;
    }

    public void Append(HttpResponse response, AuthToken token)
    {
        response.Cookies.Append(Name, token.RefreshToken, new CookieOptions(_defaultOptions)
        {
            Expires = token.RefreshExpiresAt
        });
    }

    public void Delete(HttpResponse response)
    {
        response.Cookies.Delete(Name);
    }
}
