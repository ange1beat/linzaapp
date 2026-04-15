using System.Globalization;

namespace Domain.Users.Challenges;

public interface IUserEmailChallenge
{
    Task SendEmail(string email, CultureInfo culture);

    Task Verify(string email, string passcode);
}
