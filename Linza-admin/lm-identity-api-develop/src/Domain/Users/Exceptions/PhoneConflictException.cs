using System.Globalization;

namespace Domain.Users.Exceptions;

public class PhoneConflictException : Exception
{
    private const string ErrorMsg = "Phone number '{0}' is already used";

    public PhoneConflictException(string phoneNumber) : base(
        string.Format(CultureInfo.InvariantCulture, ErrorMsg, phoneNumber))
    {
    }
}
