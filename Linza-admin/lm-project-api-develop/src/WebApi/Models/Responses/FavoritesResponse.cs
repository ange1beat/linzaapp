using Domain.Projects.Favorites;
using WebApi.Models.Authentication.Guards;

namespace WebApi.Models.Responses;

public class FavoritesResponse
{
    public IEnumerable<FavoriteInfoResponse> Favorites => _favorites
        .Select(fp =>
        {
            var response = new FavoriteInfoResponse(_guard);
            fp.Write(response);

            return response;
        })
        .ToList();

    private readonly IEnumerable<IFavoriteProjectInfo> _favorites;
    private readonly IResourceGuard _guard;

    public FavoritesResponse(
        IEnumerable<IFavoriteProjectInfo> favorites,
        IResourceGuard guard)
    {
        _favorites = favorites;
        _guard = guard;
    }
}
