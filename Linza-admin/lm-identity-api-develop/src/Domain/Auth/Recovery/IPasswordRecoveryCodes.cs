using System.Globalization;

namespace Domain.Auth.Recovery;

public interface IPasswordRecoveryCodes
{
    Task SendEmail(string email, CultureInfo culture);

    Task SendSms(string phoneNumber, CultureInfo culture);
}
