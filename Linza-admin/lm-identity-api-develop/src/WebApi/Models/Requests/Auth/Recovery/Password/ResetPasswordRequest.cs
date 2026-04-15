using Domain.Auth.Recovery;
using Microsoft.AspNetCore.Identity;
using Microsoft.Extensions.Options;
using System.ComponentModel.DataAnnotations;
using WebApi.Models.Auth;

namespace WebApi.Models.Requests.Auth.Recovery.Password;

public class ResetPasswordRequest : IValidatableObject
{
    [Required(AllowEmptyStrings = false)]
    public string RecoveryToken { get; set; } = default!;

    [Required(AllowEmptyStrings = false)]
    public string NewPassword { get; set; } = default!;

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

    public Task ResetPassword(IPasswordRecovery recovery)
    {
        return recovery.ResetPassword(RecoveryToken, NewPassword);
    }
}
