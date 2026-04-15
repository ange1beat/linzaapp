using Provider.Database.Auth;
using Provider.Database.Users;

namespace WebApi.Models.Users;

public class UserSettings : IUserSettings
{
    // ToDo: move to appsetings.
    public string AvatarScope => "users-avatar";

    public TimeSpan OtpTokenTtl => _authSettings.OtpTokenTtl;

    // ToDo: move to appsetings.
    public TimeSpan EmailInterval => TimeSpan.FromMinutes(1);

    // ToDo: move to appsetings.
    public TimeSpan SmsInterval => TimeSpan.FromMinutes(1);

    private readonly IAuthSettings _authSettings;

    public UserSettings(IAuthSettings authSettings)
    {
        _authSettings = authSettings;
    }
}
