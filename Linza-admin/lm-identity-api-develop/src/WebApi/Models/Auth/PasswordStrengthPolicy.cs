using Microsoft.AspNetCore.Identity;
using Microsoft.Extensions.Options;

namespace WebApi.Models.Auth;

public class PasswordStrengthPolicy
{
    private readonly PasswordOptions _options;

    public PasswordStrengthPolicy(IOptions<PasswordOptions> options)
    {
        _options = options.Value;
    }

    public MatchResult Match(string password)
    {
        var errors = new List<string>();

        if (_options.RequireDigit && !password.Any(char.IsDigit))
        {
            errors.Add("Password must contain at least one digit");
        }

        if (_options.RequireLowercase && !password.Any(char.IsLower))
        {
            errors.Add("Password must contain at least one lowercase letter");
        }

        if (_options.RequireNonAlphanumeric && password.All(char.IsLetterOrDigit))
        {
            errors.Add("Password must contain at least one non-alphanumeric letter");
        }

        if (_options.RequireUppercase && !password.Any(char.IsUpper))
        {
            errors.Add("Password must contain at least one uppercase letter");
        }

        if (password.Length < _options.RequiredLength)
        {
            errors.Add("Password must consist of at least 8 characters");
        }

        return new MatchResult(errors.Count == 0, errors);
    }
}

public record MatchResult(bool Succeeded, IEnumerable<string> Errors);
