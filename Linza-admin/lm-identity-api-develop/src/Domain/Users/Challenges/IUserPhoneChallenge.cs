using System.Globalization;

namespace Domain.Users.Challenges;

public interface IUserPhoneChallenge
{
    Task SendSms(string phoneNumber, CultureInfo culture);

    Task Verify(string phoneNumber, string passcode);
}
