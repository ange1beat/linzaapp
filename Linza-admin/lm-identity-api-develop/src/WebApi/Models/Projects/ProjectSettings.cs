using Domain.Projects;
using WebApi.Exceptions;

namespace WebApi.Models.Projects;

public class ProjectSettings : IProjectSettings
{
    private const string Section = "Projects";
    private readonly IConfiguration _config;

    public ProjectSettings(IConfiguration config)
    {
        _config = config;
    }

    public Uri BaseUrl => MandatoryValue<Uri>("BaseUrl");

    public string AccessToken => MandatoryValue<string>("AccessToken");

    private T MandatoryValue<T>(string name)
    {
        var key = $"{Section}:{name}";

        return _config.GetValue<T>(key)
            ?? throw new AppConfigurationException($"{key} is required");
    }
}
