using Domain.Users;

namespace Domain.Projects;

public interface IProjectMembers : IEnumerable<string>
{
    Task Add(IEnumerable<IUser> users);

    Task Remove(string userId);
}
