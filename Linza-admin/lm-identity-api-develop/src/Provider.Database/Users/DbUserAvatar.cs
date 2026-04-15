namespace Provider.Database.Users;

internal sealed class DbUserAvatar
{
    public string Id { get; set; } = null!;

    public string FileName { get; set; } = null!;

    public string? UserId { get; set; }

    public string CreatedBy { get; set; } = null!;

    public DateTime CreatedAt { get; set; }
}
