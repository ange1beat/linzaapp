using Domain.Auth.Exceptions;
using Domain.Auth.Identity;
using Domain.Rules;

namespace Domain.Users.Rules;

public class UserCanChangePasswordRule : IRule
{
    private readonly string _ownerId;
    private readonly IUserIdentity _requester;

    public UserCanChangePasswordRule(string ownerId, IUserIdentity requester)
    {
        _ownerId = ownerId;
        _requester = requester;
    }

    public bool Match()
    {
        return _requester.IsInRole(Role.Admin) || _requester.UserId == _ownerId;
    }

    public void Enforce()
    {
        if (!Match())
        {
            throw new AccessDeniedException();
        }
    }
}
