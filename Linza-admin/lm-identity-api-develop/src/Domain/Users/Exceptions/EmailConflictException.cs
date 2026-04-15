using System.Globalization;

namespace Domain.Users.Exceptions;

public class EmailConflictException : Exception
{
    private const string ErrorMsg = "Email '{0}' is already used";

    public EmailConflictException(string email) : base(
        string.Format(CultureInfo.InvariantCulture, ErrorMsg, email))
    {
    }
}
