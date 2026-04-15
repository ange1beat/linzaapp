namespace WebApi.Models.Requests.Auth;

public class RevokeTokenRequest
{
    public string RefreshToken { get; set; } = null!;
}
