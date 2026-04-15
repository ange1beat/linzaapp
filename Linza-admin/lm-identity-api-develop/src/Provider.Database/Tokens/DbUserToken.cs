using Provider.Database.Users;

namespace Provider.Database.Tokens;

internal sealed class DbUserToken
{
    public string Id { get; set; } = null!;

    public string UserId { get; set; } = null!;

    public TokenType Type { get; set; }

    public string? Data { get; set; }

    public DateTime CreatedAt { get; set; }

    public DateTime ExpiresAt { get; set; }

    public DbUser User { get; set; } = null!;
}
