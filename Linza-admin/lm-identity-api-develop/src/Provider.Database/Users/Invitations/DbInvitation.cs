using Domain.Auth.Identity;

namespace Provider.Database.Users.Invitations;

internal sealed class DbInvitation
{
    public string Id { get; set; } = null!;

    public string TenantId { get; set; } = null!;

    public string UserEmail { get; set; } = null!;

    public Role UserRole { get; set; }

    public string CreatedBy { get; set; } = null!;

    public DateTime CreatedAt { get; set; }

    public DateTime ExpiresAt { get; set; }
}
