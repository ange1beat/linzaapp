namespace Provider.Database.Projects.DbModels;

internal sealed class DbFolder
{
    public string Id { get; set; } = null!;

    public string ProjectId { get; set; } = null!;

    public string Name { get; set; } = null!;

    public string CreatedBy { get; set; } = null!;

    public DateTime CreatedAt { get; set; }

    public string UpdatedBy { get; set; } = null!;

    public DateTime UpdatedAt { get; set; }
}
