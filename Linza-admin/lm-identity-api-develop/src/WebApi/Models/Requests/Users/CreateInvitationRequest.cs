using Domain.Auth.Exceptions;
using Domain.Users.Invitations;
using System.ComponentModel.DataAnnotations;
using System.Globalization;

namespace WebApi.Models.Requests.Users;

public class CreateInvitationRequest
{
    [Required(AllowEmptyStrings = false)]
    [EmailAddress]
    public string Email { get; set; } = null!;

    [Required(AllowEmptyStrings = false)]
    public string Language { get; set; } = null!;

    public Task<IInvitation> NewInvitation(IInvitations invitations)
    {
        try
        {
            return invitations.NewInvitation(Email, new CultureInfo(Language));
        }
        catch (CultureNotFoundException)
        {
            throw new UnsupportedCultureException(Language);
        }
    }
}
