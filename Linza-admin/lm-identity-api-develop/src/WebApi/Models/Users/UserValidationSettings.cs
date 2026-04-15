using WebApi.Exceptions;

namespace WebApi.Models.Users;

public class UserValidationSettings : IUserValidationSettings
{
    private const string BaseSection = "Users";

    public string NamePattern => MandatoryValue<string>(
        "Name:Pattern",
        "Project name validation pattern is required"
    );

    public int AvatarMaxSizeKb => MandatoryValue<int>(
        "Avatar:MaxSizeKb",
        "Project avatar max size value is required"
    );

    private readonly IConfiguration _config;

    public UserValidationSettings(IConfiguration config)
    {
        _config = config;
    }

    private T MandatoryValue<T>(string name, string errorMsg)
    {
        return _config.GetValue<T>($"{BaseSection}:{name}")
            ?? throw new AppConfigurationException(errorMsg);
    }
}
