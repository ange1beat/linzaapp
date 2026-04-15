namespace Provider.Database.Projects.DbModels;

internal sealed class DbProjectAvatar
{
    public string Id { get; set; } = null!;

    public string FileName { get; set; } = null!;

    public string? ProjectId { get; set; }

    public string CreatedBy { get; set; } = null!;

    public DateTime CreatedAt { get; set; }
}
