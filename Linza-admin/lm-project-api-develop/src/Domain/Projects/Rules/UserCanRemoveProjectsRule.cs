using Domain.Authentication;
using Domain.Exceptions;
using Domain.Rules;

namespace Domain.Projects.Rules;

public class UserCanRemoveProjectsRule : IRule
{
    private const string ErrorMessage = "Requester has no permissions to remove project";

    private readonly IUserIdentity _requester;

    public UserCanRemoveProjectsRule(IUserIdentity requester)
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
