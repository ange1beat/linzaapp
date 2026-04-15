using System.ComponentModel.DataAnnotations;
using System.Text.RegularExpressions;
using WebApi.Models.Projects;

namespace WebApi.Attributes;

[AttributeUsage(AttributeTargets.Property | AttributeTargets.Field)]
public class ProjectNameAttribute : ValidationAttribute
{
    protected override ValidationResult? IsValid(
        object? value,
        ValidationContext validationContext)
    {
        if (value is null)
        {
            return ValidationResult.Success;
        }

        var validationSettings = validationContext
            .GetRequiredService<IProjectValidationSettings>();

        var projectName = value.ToString() ?? string.Empty;
        var nameRegex = new Regex(validationSettings.NamePattern);
        if (nameRegex.IsMatch(projectName))
        {
            return ValidationResult.Success;
        }

        return new ValidationResult(ErrorMessage ?? "Project name has invalid format");
    }
}
