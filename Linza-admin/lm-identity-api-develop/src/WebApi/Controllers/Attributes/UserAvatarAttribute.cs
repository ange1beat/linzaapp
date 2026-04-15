using System.ComponentModel.DataAnnotations;
using WebApi.Models.Users;

namespace WebApi.Controllers.Attributes;

public class UserAvatarAttribute : ValidationAttribute
{
    private static readonly HashSet<string> _allowedTypes = new()
    {
        "image/jpeg", "image/jpg", "image/png"
    };

    protected override ValidationResult? IsValid(
        object? value,
        ValidationContext validationContext)
    {
        if (value is null)
        {
            return ValidationResult.Success;
        }

        if (value is not IFormFile file)
        {
            throw new ArgumentException("Invalid value", nameof(value));
        }

        var validationSettings = validationContext
            .GetRequiredService<IUserValidationSettings>();

        // 1 KB = 1000 bytes
        var maxAvatarSizeBytes = validationSettings.AvatarMaxSizeKb * 1000;

        if (file.Length > maxAvatarSizeBytes)
        {
            return new ValidationResult(
                $"Avatar size must not exceed {validationSettings.AvatarMaxSizeKb} kB"
            );
        }

        if (!_allowedTypes.Contains(file.ContentType))
        {
            return new ValidationResult(
                $"Avatar must be an image in format: {string.Join("/", _allowedTypes)}"
            );
        }

        return ValidationResult.Success;
    }
}
