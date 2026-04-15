using WebApi.Exceptions;

namespace WebApi.Models.Authentication.Guards;

public class ResourceGuardSettings : IResourceGuardSettings
{
    private const string Section = "Authentication:ResourceGuard";

    public string SecretKey => MandatoryValue<string>("SecretKey");

    private readonly IConfiguration _config;

    public ResourceGuardSettings(IConfiguration config)
    {
        _config = config;
    }

    private T MandatoryValue<T>(string name)
    {
        var key = $"{Section}:{name}";

        return _config.GetValue<T>(key)
            ?? throw new ConfigurationException($"{key} is required");
    }
}
