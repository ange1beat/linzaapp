using System.Globalization;

namespace Domain.Users.Exceptions;

public class UserNotFoundException : Exception
{
    private const string MessageTemplate = "User - '{0}' is not found!";

    public UserNotFoundException(string userId) : base(
        string.Format(CultureInfo.InvariantCulture, MessageTemplate, userId))
    {
    }
}
