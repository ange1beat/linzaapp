namespace Provider.Database.Projects.DbModels;

internal class DbFavoriteProject
{
    public string ProjectId { get; set; } = null!;

    public string UserId { get; set; } = null!;

    public string TenantId { get; set; } = null!;

    public DateTime CreatedAt { get; set; }
}
