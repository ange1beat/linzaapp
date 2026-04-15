using Domain.Users;
using System.ComponentModel.DataAnnotations;

namespace WebApi.Models.Requests.Users;

public class RenameUserRequest
{
    [Required(AllowEmptyStrings = false)]
    [StringLength(50, MinimumLength = 1)]
    public string FirstName { get; set; } = null!;

    [Required(AllowEmptyStrings = false)]
    [StringLength(50, MinimumLength = 1)]
    public string LastName { get; set; } = null!;

    public Task RenameUser(IUser user)
    {
        var details = new UserDetails();
        user.Write(details);

        return user.UpdateDetails(
            details.WithName(FirstName, LastName)
        );
    }
}
