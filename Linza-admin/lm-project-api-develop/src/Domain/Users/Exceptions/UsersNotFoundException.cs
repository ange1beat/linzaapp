using System.Globalization;

namespace Domain.Users.Exceptions;

public class UsersNotFoundException : Exception
{
    private const string MessageTemplate = "Users [{0}] are not found";

    public readonly IEnumerable<string> UserIds;

    public UsersNotFoundException(IReadOnlyCollection<string> userIds) : base(
        string.Format(
            CultureInfo.InvariantCulture,
            MessageTemplate,
            string.Join(',', userIds)))
    {
        UserIds = userIds;
    }
}
