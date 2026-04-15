using Domain.Authentication;

namespace Domain.Users;

public interface IUsers
{
    Task<IUser> User(string userId, IUserIdentity requester);

    Task<IReadOnlyCollection<IUser>> AllUsers(
        IEnumerable<string> userIds,
        IUserIdentity requester
    );

    Task<IReadOnlyCollection<IUser>> Supervisors(IUserIdentity requester);
}
