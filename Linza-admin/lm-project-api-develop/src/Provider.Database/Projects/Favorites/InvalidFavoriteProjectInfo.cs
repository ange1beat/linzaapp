using Domain.Media;
using Domain.Projects.Favorites;
using Provider.Database.Projects.DbModels;

namespace Provider.Database.Projects.Favorites;

internal class InvalidFavoriteProjectInfo : IFavoriteProjectInfo
{
    private readonly DbFavoriteProject _entity;

    public InvalidFavoriteProjectInfo(DbFavoriteProject entity)
    {
        _entity = entity;
    }

    public void Write(IMedia media)
    {
        media.Write("Id", _entity.ProjectId);
        media.Write("FavoritedAt", _entity.CreatedAt);
        media.Write("IsAvailable", false);
    }
}
