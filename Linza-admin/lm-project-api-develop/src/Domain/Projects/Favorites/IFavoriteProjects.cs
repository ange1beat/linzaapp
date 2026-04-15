using Domain.Authentication;

namespace Domain.Projects.Favorites;

public interface IFavoriteProjects
{
    Task<IReadOnlyList<IFavoriteProjectInfo>> All(IUserIdentity requester);

    Task Put(string projectId, IUserIdentity requester);

    Task Remove(string projectId, IUserIdentity requester);
}
