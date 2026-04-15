using Domain.Authentication;
using Domain.Exceptions;
using Domain.Rules;
using Domain.Users;
using System.Globalization;

namespace Domain.Projects.Rules;

public class UserCanAccessUsersRule : IRule
{
    private const string ErrorMessage = "Requester has no permissions to access users - [{0}]";

    private readonly IEnumerable<IUser> _users;
    private readonly IUserIdentity _requester;

    public UserCanAccessUsersRule(IUserIdentity requester, params IUser[] users) : this(
        requester, users.ToList())
    {
    }

    public UserCanAccessUsersRule(IUserIdentity requester, IEnumerable<IUser> users)
    {
        _users = users;
        _requester = requester;
    }

    public bool Match()
    {
        if (_requester.IsAdmin())
        {
            return true;
        }

        return _requester.IsSupervisor() &&
            _users.Any(m => m.TenantId != _requester.TenantId);
    }

    public void Enforce()
    {
        if (Match()) return;

        var unavailableUserIds = _users
            .Where(u => u.TenantId != _requester.TenantId)
            .Select(u => u.Id)
            .ToList();

        if (unavailableUserIds.Count != 0)
        {
            throw new AccessDeniedException(_requester, string.Format(
                CultureInfo.InvariantCulture,
                ErrorMessage,
                string.Join(',', unavailableUserIds)
            ));
        }
    }
}
