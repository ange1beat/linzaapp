using Domain.Users;
using Domain.Users.Challenges;
using System.ComponentModel.DataAnnotations;

namespace WebApi.Models.Requests.Users;

public class ChangeMyPhoneRequest
{
    [Required(AllowEmptyStrings = false)]
    [Phone]
    public string PhoneNumber { get; set; } = null!;

    [Required(AllowEmptyStrings = false)]
    public string VerificationCode { get; set; } = null!;

    public async Task ChangePhone(IUser user, IUserPhoneChallenge challenge)
    {
        await challenge.Verify(PhoneNumber, VerificationCode);

        var details = new UserDetails();
        user.Write(details);

        await user.UpdateDetails(
            details.WithPhone(PhoneNumber)
        );
    }
}
