using Domain.Authentication;
using Domain.Users;

namespace Domain.Projects.Membership;

public interface IProjectsMembership
{
    Task<IEnumerable<string>> ProjectIds(IUserIdentity requester);

    Task<IEnumerable<string>> ProjectIds(IUser user, IUserIdentity requester);

    Task Assign(IUser user, IEnumerable<string> projectIds, IUserIdentity requester);

    Task Remove(IUser user, IEnumerable<string> projectIds, IUserIdentity requester);

    Task Remove(IUser user, IUserIdentity requester);
}
