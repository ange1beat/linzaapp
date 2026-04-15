using Domain.Auth.Exceptions;
using Domain.Auth.Identity;
using Domain.Rules;

namespace Domain.Users.Rules;

public class UserCanManageInvitationRule : IRule
{
    private readonly IUserIdentity _requester;

    public UserCanManageInvitationRule(IUserIdentity requester)
    {
        _requester = requester;
    }

    public bool Match()
    {
        return _requester.IsInRole(Role.Admin) || _requester.IsInRole(Role.Supervisor);
    }

    public void Enforce()
    {
        if (!Match())
        {
            throw new AccessDeniedException();
        }
    }
}
