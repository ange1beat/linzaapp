using WebApi.Exceptions;

namespace WebApi.Models.Authentication;

public class JwtSettings
{
    private const string Section = "Authentication:JWT";

    public string PublicKey => MandatoryValue<string>("PublicKey");

    public string Issuer => MandatoryValue<string>("Issuer");

    public string Audience => MandatoryValue<string>("Audience");

    private readonly IConfiguration _config;

    public JwtSettings(IConfiguration config)
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
