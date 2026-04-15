namespace Provider.Database.Projects.DbModels;

internal sealed class DbProjectMember
{
    public string ProjectId { get; set; } = null!;

    public string UserId { get; set; } = null!;

    public string CreatedBy { get; set; } = null!;

    public DateTime CreatedAt { get; set; }

    public DbProject Project { get; set; } = null!;
}
