using Domain.Auth;
using Provider.Database.Auth;
using System.Xml;
using WebApi.Exceptions;

namespace WebApi.Models.Auth;

public class AuthSettings : IAuthSettings
{
    private const string Section = "Authentication";

    // ToDo: move to appsetings.
    public int MaxFailedAccessAttempts => 3;

    // ToDo: move to appsetings.
    public TimeSpan LockoutDuration => TimeSpan.FromMinutes(5);

    // ToDo: move to appsetings.
    public TimeSpan OtpTokenTtl => TimeSpan.FromMinutes(5);

    public TimeSpan StateTokenTtl => XmlConvert.ToTimeSpan(
        MandatoryValue<string>("StateTokenExpirationTime")
    );

    public TimeSpan RefreshTokenTtl => XmlConvert.ToTimeSpan(
        MandatoryValue<string>("RefreshTokenExpirationTime")
    );

    public IJwtSettings AccessToken => new JwtSettings(_config);

    private readonly IConfiguration _config;

    public AuthSettings(IConfiguration config)
    {
        _config = config;
    }

    private T MandatoryValue<T>(string name)
    {
        var key = $"{Section}:{name}";

        return _config.GetValue<T>(key)
            ?? throw new AppConfigurationException($"{key} is required");
    }
}
