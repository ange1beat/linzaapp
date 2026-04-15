using Domain.Users;
using Domain.Users.Challenges;
using Domain.Users.Exceptions;
using System.ComponentModel.DataAnnotations;
using System.Globalization;

namespace WebApi.Models.Requests.Users;

public class PhoneChangeRequest : IValidatableObject
{
    [Required(AllowEmptyStrings = false)]
    [Phone]
    public string PhoneNumber { get; set; } = null!;

    [Required(AllowEmptyStrings = false)]
    public string Language { get; set; } = null!;

    private CultureInfo Culture => new(Language);

    public IEnumerable<ValidationResult> Validate(ValidationContext validationContext)
    {
        var errors = new List<ValidationResult>();
        try
        {
            _ = new CultureInfo(Language);
        }
        catch (CultureNotFoundException)
        {
            errors.Add(new ValidationResult("Unsupported language"));
        }

        return errors;
    }

    public async Task Challenge(IUsers users, IUserPhoneChallenge challenge)
    {
        if (await users.Search().WithPhone(PhoneNumber).Any())
        {
            throw new PhoneConflictException(PhoneNumber);
        }

        await challenge.SendSms(PhoneNumber, Culture);
    }
}
