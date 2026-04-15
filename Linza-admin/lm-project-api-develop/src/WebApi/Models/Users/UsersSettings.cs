using WebApi.Models.Settings;

namespace WebApi.Models.Users;

public class UsersSettings : ConfigSettingsBase
{
    private const string Section = "Application:Users";

    public Uri ApiBaseUrl => new(MandatoryValue<string>("ApiBaseUrl"));

    public UsersSettings(IConfiguration config) : base(config, Section)
    {
    }
}
