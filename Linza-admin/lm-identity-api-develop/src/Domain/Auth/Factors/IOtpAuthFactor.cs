using System.Globalization;

namespace Domain.Auth.Factors;

public interface IOtpAuthFactor
{
    Task ChallengeByEmail(string stateToken, CultureInfo culture);

    Task ChallengeBySms(string stateToken, CultureInfo culture);

    Task<IAuthState> Verify(string stateToken, string passcode);
}
