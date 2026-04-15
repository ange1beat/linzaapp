namespace WebApi.Models.Projects;

public interface IProjectValidationSettings
{
    string NamePattern { get; }

    int AvatarMaxSizeKb { get; }
}
