using Domain.Auth.Recovery;
using System.ComponentModel.DataAnnotations;

namespace WebApi.Models.Requests.Auth.Recovery.Password;

public class GetRecoveryTokenRequest
{
    [Required(AllowEmptyStrings = false)]
    public string Login { get; set; } = default!;

    [Required(AllowEmptyStrings = false)]
    public string RecoveryCode { get; set; } = default!;

    public Task<string> RecoveryToken(IPasswordRecovery recovery)
    {
        return recovery.RecoveryToken(Login, RecoveryCode);
    }
}
