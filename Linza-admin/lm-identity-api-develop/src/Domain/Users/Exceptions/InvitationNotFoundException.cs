using System.Globalization;

namespace Domain.Users.Exceptions;

public class InvitationNotFoundException : Exception
{
    private const string ErrorMsg = "Invitation '{0}' is not found";

    public InvitationNotFoundException(string invitationId) : base(
        string.Format(CultureInfo.InvariantCulture, ErrorMsg, invitationId))
    {
    }
}
