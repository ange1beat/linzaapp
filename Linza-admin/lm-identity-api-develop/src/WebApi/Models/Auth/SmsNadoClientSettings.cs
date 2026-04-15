using Domain.Cellular;
using WebApi.Exceptions;

namespace WebApi.Models.Auth;

public class SmsNadoClientSettings : ISmsNadoClientSettings
{
    private const string Section = "Cellular";

    private readonly IConfiguration _config;

    public SmsNadoClientSettings(IConfiguration config)
    {
        _config = config;
    }

    public Uri BaseUrl => new(MandatoryValue<string>("BaseUrl"));

    public string User => MandatoryValue<string>("User");

    public string Password => MandatoryValue<string>("Password");

    public string Sender => MandatoryValue<string>("Sender");

    private T MandatoryValue<T>(string name)
    {
        var key = $"{Section}:{name}";

        return _config.GetValue<T>(key)
            ?? throw new AppConfigurationException($"{key} is required");
    }
}
