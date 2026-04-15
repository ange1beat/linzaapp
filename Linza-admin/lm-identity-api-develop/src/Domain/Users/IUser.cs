using Domain.Auth.Identity;
using Domain.Media;

namespace Domain.Users;

public interface IUser : IWritable
{
    string Id { get; }

    bool IsPasswordMatch(string password);

    Task AttachAvatar(Stream content, string extension);

    Task ChangePassword(string password);

    Task ChangeRoles(IEnumerable<Role> roles);

    Task RemoveAvatar();

    Task UpdateDetails(UserDetails details);
}
