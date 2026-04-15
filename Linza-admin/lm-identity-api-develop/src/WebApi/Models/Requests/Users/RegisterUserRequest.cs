using Domain.Users;
using Microsoft.AspNetCore.Identity;
using Microsoft.Extensions.Options;
using System.ComponentModel.DataAnnotations;
using WebApi.Models.Auth;

namespace WebApi.Models.Requests.Users;

public class RegisterUserRequest : IValidatableObject
{
    [Required(AllowEmptyStrings = false)]
    public string InvitationId { get; set; } = null!;

    [Required(AllowEmptyStrings = false)]
    [StringLength(50, MinimumLength = 1)]
    public string FirstName { get; set; } = null!;

    [Required(AllowEmptyStrings = false)]
    [StringLength(50, MinimumLength = 1)]
    public string LastName { get; set; } = null!;

    [Required(AllowEmptyStrings = false)]
    [MaxLength(50)]
    public string Password { get; set; } = null!;

    public IEnumerable<ValidationResult> Validate(ValidationContext ctx)
    {
        var policy = new PasswordStrengthPolicy(
            ctx.GetRequiredService<IOptions<PasswordOptions>>()
        );

        MatchResult result = policy.Match(Password);

        return result.Errors.Select(error =>
            new ValidationResult(error, new[] { nameof(Password) })
        );
    }

    public Task<IUser> NewUser(IUsers users)
    {
        return users.NewUser(InvitationId, FirstName, LastName, Password);
    }
}
