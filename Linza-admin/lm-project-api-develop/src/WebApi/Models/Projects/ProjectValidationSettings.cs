using WebApi.Models.Settings;

namespace WebApi.Models.Projects;

public class ProjectValidationSettings : ConfigSettingsBase, IProjectValidationSettings
{
    private const string Section = "Application:Projects";

    public string NamePattern => MandatoryValue<string>("Name:Pattern");

    public int AvatarMaxSizeKb => MandatoryValue<int>("Avatar:MaxSizeKb");

    public ProjectValidationSettings(IConfiguration config) : base(config, Section)
    {
    }
}
