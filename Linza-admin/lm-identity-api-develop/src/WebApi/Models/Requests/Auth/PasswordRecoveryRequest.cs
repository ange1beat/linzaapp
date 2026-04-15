using System.ComponentModel.DataAnnotations;

namespace WebApi.Models.Requests.Auth;

public class PasswordRecoveryRequest
{
    [Required(AllowEmptyStrings = false)]
    public string StateToken { get; set; } = null!;

    [Required]
    public string NewPassword { get; set; } = null!;
}
