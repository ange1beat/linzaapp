using Domain.Media;
using Domain.Projects;
using Domain.Projects.Favorites;

namespace Provider.Database.Projects.Favorites;

internal class FavoriteProjectInfo : IFavoriteProjectInfo
{
    private readonly IProject _project;
    private readonly DateTime _favoritedAt;

    public FavoriteProjectInfo(IProject project, DateTime favoritedAt)
    {
        _project = project;
        _favoritedAt = favoritedAt;
    }

    public void Write(IMedia media)
    {
        _project.Write(new ProjectedMedia(media, new HashSet<string>
        {
            "Id",
            "Name",
            "AvatarUrl"
        }));

        media.Write("FavoritedAt", _favoritedAt);
        media.Write("IsAvailable", true);
    }
}
