using Provider.Database.Projects;
using WebApi.Models.Settings;

namespace WebApi.Models.Projects;

public class ProjectSettings : ConfigSettingsBase, IProjectSettings
{
    private const string Section = "Application:Projects";

    public string AvatarScope => MandatoryValue<string>("Avatar:FileScope");

    public ProjectSettings(IConfiguration config) : base(config, Section)
    {
    }
}
