using Domain.Auth.Identity;

namespace Provider.Database.Users;

internal sealed class DbUserRole
{
    public string UserId { get; set; } = null!;

    public Role Role { get; set; }
}
