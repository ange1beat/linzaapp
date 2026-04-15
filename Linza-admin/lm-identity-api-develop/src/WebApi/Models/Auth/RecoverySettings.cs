using Provider.Database.Auth;
using Provider.Database.Auth.Recovery;

namespace WebApi.Models.Auth;

public class RecoverySettings : IRecoverySettings
{
    public TimeSpan OtpTokenTtl => _authSettings.OtpTokenTtl;

    public TimeSpan RecoveryTokenTtl => _authSettings.StateTokenTtl;

    private readonly IAuthSettings _authSettings;

    public RecoverySettings(IAuthSettings authSettings)
    {
        _authSettings = authSettings;
    }
}
