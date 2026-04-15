using Domain.Authentication;
using Domain.Exceptions;
using Domain.Rules;

namespace Domain.Projects.Rules;

public class UserCanUpdateProjectRule : IRule
{
    private const string ErrorMessage = "Requester has no permission to update project";

    private readonly IUserIdentity _requester;

    public UserCanUpdateProjectRule(IUserIdentity requester)
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
