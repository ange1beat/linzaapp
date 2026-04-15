using Domain.Authentication;
using Domain.Exceptions;
using Domain.Rules;

namespace Domain.Users.Rules;

public class UserCanRequestUsersRule : IRule
{
    private const string ErrorMessage = "User has no permissions to access tennat users";

    private readonly IUserIdentity _user;

    public UserCanRequestUsersRule(IUserIdentity user)
    {
        _user = user;
    }

    public bool Match()
    {
        return _user.IsAdmin() || _user.IsSupervisor();
    }

    public void Enforce()
    {
        if (!Match())
        {
            throw new AccessDeniedException(_user, ErrorMessage);
        }
    }
}
