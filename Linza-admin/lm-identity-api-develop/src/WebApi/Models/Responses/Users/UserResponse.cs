using Domain.Auth.Identity;
using Domain.Media;

namespace WebApi.Models.Responses.Users;

public class UserResponse : ReflectedMedia
{
    public string Id { get; set; } = default!;

    public string TenantId { get; set; } = default!;

    public string FirstName { get; set; } = default!;

    public string LastName { get; set; } = default!;

    public string Email { get; set; } = default!;

    public string? PhoneNumber { get; set; }

    public string? TelegramUsername { get; set; }

    public string? AvatarUrl { get; set; }

    public IEnumerable<Role> Roles { get; set; } = default!;

    public DateTime? LastLoginDate { get; set; }
}
