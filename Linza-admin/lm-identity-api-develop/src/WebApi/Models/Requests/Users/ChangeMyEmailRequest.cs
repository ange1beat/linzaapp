using Domain.Users;
using Domain.Users.Challenges;
using System.ComponentModel.DataAnnotations;

namespace WebApi.Models.Requests.Users;

public class ChangeMyEmailRequest
{
    [Required(AllowEmptyStrings = false)]
    [EmailAddress]
    public string Email { get; set; } = null!;

    [Required(AllowEmptyStrings = false)]
    public string VerificationCode { get; set; } = null!;

    public async Task ChangeEmail(IUser user, IUserEmailChallenge challenge)
    {
        await challenge.Verify(Email, VerificationCode);

        var details = new UserDetails();
        user.Write(details);

        await user.UpdateDetails(
            details.WithEmail(Email)
        );
    }
}
