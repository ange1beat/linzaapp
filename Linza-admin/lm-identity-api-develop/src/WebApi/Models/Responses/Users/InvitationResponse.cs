using Domain.Media;

namespace WebApi.Models.Responses.Users;

public class InvitationResponse : ReflectedMedia
{
    public string Id { get; set; } = default!;

    public string UserEmail { get; set; } = default!;

    public DateTime CreatedAt { get; set; }

    public DateTime ExpiresAt { get; set; }
}
