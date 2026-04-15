namespace Domain.Projects;

public interface IProjectSettings
{
    Uri BaseUrl { get; }

    string AccessToken { get; }
}
