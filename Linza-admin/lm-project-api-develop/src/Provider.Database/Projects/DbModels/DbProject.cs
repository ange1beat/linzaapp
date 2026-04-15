namespace Provider.Database.Projects.DbModels;

internal sealed class DbProject
{
    public string Id { get; set; } = null!;

    public string TenantId { get; set; } = null!;

    public string Name { get; set; } = null!;

    public DbProjectAvatar? Avatar { get; set; }

    public List<DbProjectMember> Members { get; set; } = new();

    public string CreatedBy { get; set; } = null!;

    public DateTime CreatedAt { get; set; }

    public string UpdatedBy { get; set; } = null!;

    public DateTime UpdatedAt { get; set; }

    public uint RowVersion { get; set; }
}
