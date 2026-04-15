using Domain.Auth.Identity;

namespace WebApi.Models.Auth;

public class AuthContext : IAuthContext
{
    private readonly IHttpContextAccessor _contextAccessor;

    public AuthContext(IHttpContextAccessor contextAccessor)
    {
        _contextAccessor = contextAccessor;
    }

    public IUserIdentity LoggedInIdentity()
    {
        return new ApiUserIdentity(
            _contextAccessor.HttpContext ?? throw new InvalidOperationException(
                "Http context is required"
            )
        );
    }
}
