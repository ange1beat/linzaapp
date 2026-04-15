using Domain.Auth.Exceptions;
using Domain.Users;
using Microsoft.AspNetCore.Identity;
using Microsoft.Extensions.Options;
using System.ComponentModel.DataAnnotations;
using WebApi.Models.Auth;

namespace WebApi.Models.Requests.Users;

public class ChangeMyPasswordRequest : IValidatableObject
{
    [Required(AllowEmptyStrings = false)]
    public string CurrentPassword { get; set; } = null!;

    [Required(AllowEmptyStrings = false)]
    public string NewPassword { get; set; } = null!;

    public IEnumerable<ValidationResult> Validate(ValidationContext ctx)
    {
        var policy = new PasswordStrengthPolicy(
            ctx.GetRequiredService<IOptions<PasswordOptions>>()
        );

        MatchResult result = policy.Match(NewPassword);

        return result.Errors.Select(error =>
            new ValidationResult(error, new[] { nameof(NewPassword) })
        );
    }

    public Task ChangePassword(IUser user)
    {
        if (!user.IsPasswordMatch(CurrentPassword))
        {
            throw new AccessDeniedException();
        }

        return user.ChangePassword(NewPassword);
    }
}
