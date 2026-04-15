using Domain.Authentication;
using Domain.Users;

namespace Provider.Identity.Users;

internal class User : IUser
{
    public string Id => _user.Id;

    public string TenantId => _requester.TenantId;

    private readonly UserDto _user;
    private readonly IUserIdentity _requester;

    public User(UserDto user, IUserIdentity requester)
    {
        _user = user;
        _requester = requester;
    }

    public bool IsSupervisor() => _user.Roles.Contains(UserRole.Supervisor);
}
