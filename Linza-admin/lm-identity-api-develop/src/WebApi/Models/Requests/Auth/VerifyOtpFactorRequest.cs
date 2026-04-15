using Domain.Auth;
using Domain.Auth.Factors;
using System.ComponentModel.DataAnnotations;

namespace WebApi.Models.Requests.Auth;

public class VerifyOtpFactorRequest
{
    [Required(AllowEmptyStrings = false)]
    public string StateToken { get; set; } = null!;

    [Required(AllowEmptyStrings = false)]
    public string Passcode { get; set; } = null!;

    public Task<IAuthState> Verify(IOtpAuthFactor otpFactor)
    {
        return otpFactor.Verify(StateToken, Passcode);
    }
}
