using Domain.Auth.Exceptions;
using Domain.Auth.Recovery;
using System.ComponentModel.DataAnnotations;
using System.Globalization;

namespace WebApi.Models.Requests.Auth.Recovery.Password;

public class EmailChallengeRequest
{
    [Required(AllowEmptyStrings = false)]
    [EmailAddress]
    public string Email { get; set; } = default!;

    [Required(AllowEmptyStrings = false)]
    public string Language { get; set; } = default!;

    public Task SendCode(IPasswordRecoveryCodes recoveryCodes)
    {
        return recoveryCodes.SendEmail(Email, Culture());
    }

    private CultureInfo Culture()
    {
        try
        {
            return new CultureInfo(Language);
        }
        catch (CultureNotFoundException)
        {
            throw new UnsupportedCultureException(Language);
        }
    }
}
