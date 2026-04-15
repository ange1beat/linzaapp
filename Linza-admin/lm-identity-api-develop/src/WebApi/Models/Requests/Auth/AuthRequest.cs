using Domain.Auth;
using System.ComponentModel.DataAnnotations;

namespace WebApi.Models.Requests.Auth;

public class AuthRequest
{
    [Required(AllowEmptyStrings = false)]
    public string Login { get; set; } = null!;

    [Required]
    public string Password { get; set; } = null!;

    public Task<IAuthState> Authenticate(IBaseAuth baseAuth)
    {
        return baseAuth.Authenticate(Login, Password);
    }
}
