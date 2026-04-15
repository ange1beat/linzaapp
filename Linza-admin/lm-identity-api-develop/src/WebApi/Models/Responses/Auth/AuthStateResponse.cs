using Domain.Media;

namespace WebApi.Models.Responses.Auth;

public class AuthStateResponse : ReflectedMedia
{
    public UserInfoDto User { get; set; } = default!;

    public string StateToken { get; set; } = default!;

    public DateTime ExpiresAt { get; set; }
}

public class UserInfoDto : ReflectedMedia
{
    public string Id { get; set; } = default!;

    public string Email { get; set; } = default!;

    public string? PhoneNumber { get; set; }
}
