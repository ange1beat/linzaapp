using System.Globalization;

namespace Domain.Users.Invitations;

public interface IInvitations
{
    Task<IInvitation> NewInvitation(string email, CultureInfo culture);

    Task<IInvitation> Invitation(string invitationId);

    Task Remove(string invitationId);
}
