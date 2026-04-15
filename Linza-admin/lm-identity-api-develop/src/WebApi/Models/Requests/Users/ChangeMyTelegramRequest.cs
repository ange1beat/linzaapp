using Domain.Users;
using System.ComponentModel.DataAnnotations;

namespace WebApi.Models.Requests.Users;

public class ChangeMyTelegramRequest
{
    [Required(AllowEmptyStrings = false)]

    [RegularExpression("^@?\\w{5,32}$")]
    public string Username { get; set; } = null!;

    public Task ChangeTelegram(IUser user)
    {
        var details = new UserDetails();
        user.Write(details);

        return user.UpdateDetails(
            details.WithTelegram(Username)
        );
    }
}
