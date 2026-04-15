namespace Provider.Database.Users;

internal sealed class DbUser
{
    public string Id { get; set; } = default!;

    public string TenantId { get; set; } = null!;

    public string FirstName { get; set; } = null!;

    public string LastName { get; set; } = null!;

    public string Email { get; set; } = null!;

    public string? PhoneNumber { get; set; }

    public string? TelegramUsername { get; set; }

    public DbUserAvatar? Avatar { get; set; }

    public string PasswordHash { get; set; } = null!;

    public int AccessFailedCount { get; set; }

    public DateTime? LockoutEndDate { get; set; }

    public DateTime? LastFailedAccessDate { get; set; }

    public DateTime? LastLoginDate { get; set; }

    public DateTime CreatedAt { get; set; }

    public DateTime UpdatedAt { get; set; }

    public List<DbUserRole> Roles { get; set; } = default!;
}
