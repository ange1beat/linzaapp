using Domain.Auth.Exceptions;
using Domain.Auth.Identity;
using Domain.Rules;

namespace Domain.Users.Rules;

public class UserCanChangeRolesRule : IRule
{
    private readonly string _tenantId;
    private readonly IUserIdentity _requester;

    public UserCanChangeRolesRule(string tenantId, IUserIdentity requester)
    {
        _tenantId = tenantId;
        _requester = requester;
    }

    public bool Match()
    {
        return _requester.IsInRole(Role.Admin) ||
            (_requester.IsInRole(Role.Supervisor) && _tenantId == _requester.TenantId);
    }

    public void Enforce()
    {
        if (!Match())
        {
            throw new AccessDeniedException();
        }
    }
}
