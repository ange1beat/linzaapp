using System.Globalization;

namespace Provider.Database.Users.Invitations;

public interface IInvitationSettings
{
    TimeSpan InvitationTtl { get; }

    Uri RegistrationLink(string invitationId, CultureInfo culture);
}
