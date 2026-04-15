using Domain.Auth;

namespace Provider.Database.Auth;

public interface IAuthSettings
{
    int MaxFailedAccessAttempts { get; }

    TimeSpan LockoutDuration { get; }

    TimeSpan StateTokenTtl { get; }

    TimeSpan RefreshTokenTtl { get; }

    TimeSpan OtpTokenTtl { get; }

    IJwtSettings AccessToken { get; }
}
