using Domain.Auth.Exceptions;
using Domain.Auth.Factors;
using System.ComponentModel.DataAnnotations;
using System.Globalization;

namespace WebApi.Models.Requests.Auth;

public class OtpFactorChallengeRequest
{
    [Required(AllowEmptyStrings = false)]
    public string StateToken { get; set; } = default!;

    [Required(AllowEmptyStrings = false)]
    public string Language { get; set; } = default!;

    public Task ChallengeByEmail(IOtpAuthFactor otpFactor)
    {
        return otpFactor.ChallengeByEmail(StateToken, Culture());
    }

    public Task ChallengeBySms(IOtpAuthFactor otpFactor)
    {
        return otpFactor.ChallengeBySms(StateToken, Culture());
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
