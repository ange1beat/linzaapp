using Domain.Authentication;
using Domain.Exceptions;
using Domain.Rules;

namespace Domain.Projects.Rules;

public class UserCanAccessProjectMembersRule : IRule
{
    private const string ErrorMessage = "Requester has no permissions to access project members";

    private readonly IUserIdentity _requester;

    public UserCanAccessProjectMembersRule(IUserIdentity requester)
    {
        _requester = requester;
    }

    public bool Match()
    {
        return _requester.IsAdmin() || _requester.IsSupervisor();
    }

    public void Enforce()
    {
        if (!Match())
        {
            throw new AccessDeniedException(_requester, ErrorMessage);
        }
    }
}
