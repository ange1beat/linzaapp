namespace Domain.Projects;

public interface IProjects
{
    public Task<IReadOnlyCollection<string>> ProjectIds(string userId);
}
