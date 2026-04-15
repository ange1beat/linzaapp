using Domain.Media;
using WebApi.Models.Authentication.Guards;

namespace WebApi.Models.Responses;

public class FavoriteInfoResponse : ReflectedMedia
{
    public string Id { get; set; } = null!;

    public string? Name { get; set; }

    public Uri? AvatarUrl { get; set; }

    public DateTime FavoritedAt { get; set; }

    public bool IsAvailable { get; set; }

    private readonly IResourceGuard _guard;

    public FavoriteInfoResponse(IResourceGuard guard)
    {
        _guard = guard;
    }

    public override void Write<T>(string name, T value)
    {
        if (name.Equals(nameof(AvatarUrl)) && value is not null)
        {
            AvatarUrl = _guard.SignedUrl((value as Uri)!);
            return;
        }

        base.Write(name, value);
    }
}
