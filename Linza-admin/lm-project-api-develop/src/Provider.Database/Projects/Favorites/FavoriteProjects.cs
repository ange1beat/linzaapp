using Domain.Authentication;
using Domain.Projects;
using Domain.Projects.Exceptions;
using Domain.Projects.Favorites;
using Microsoft.EntityFrameworkCore;
using Provider.Database.Context;
using Provider.Database.Projects.DbModels;

namespace Provider.Database.Projects.Favorites;

public class FavoriteProjects : IFavoriteProjects
{
    private readonly IFavoritesSettings _settings;
    private readonly IProjects _projects;
    private readonly DatabaseContext _dbCtx;

    public FavoriteProjects(
        IFavoritesSettings settings,
        IProjects projects,
        DatabaseContext dbCtx)
    {
        _settings = settings;
        _projects = projects;
        _dbCtx = dbCtx;
    }

    public async Task<IReadOnlyList<IFavoriteProjectInfo>> All(IUserIdentity requester)
    {
        var favorites = await _dbCtx.Set<DbFavoriteProject>()
            .Where(fp =>
                fp.UserId == requester.UserId &&
                fp.TenantId == requester.TenantId
            )
            .ToListAsync();

        var favoriteProjects = await _projects.Search(requester)
            .WithIds(favorites.Select(fp => fp.ProjectId).ToArray())
            .Projects();

        var projectsMap = favoriteProjects.ToDictionary(fp => fp.Id, fp => fp);

        var result = favorites.Select<DbFavoriteProject, IFavoriteProjectInfo>(fp =>
        {
            if (projectsMap.TryGetValue(fp.ProjectId, out var project))
            {
                return new FavoriteProjectInfo(project, fp.CreatedAt);
            }

            return new InvalidFavoriteProjectInfo(fp);
        });

        return result.ToList();
    }

    public async Task Put(string projectId, IUserIdentity requester)
    {
        if (!await _projects.Search(requester).WithIds(projectId).Any())
        {
            throw new ProjectNotFoundException(projectId);
        }

        var userFavorites = await _dbCtx.Set<DbFavoriteProject>()
            .Where(fp =>
                fp.UserId == requester.UserId &&
                fp.TenantId == requester.TenantId
            )
            .ToListAsync();

        if (userFavorites.Any(fp => fp.ProjectId == projectId))
        {
            return;
        }

        var maxSizeLimit = _settings.MaxSize;
        if (userFavorites.Count >= maxSizeLimit)
        {
            throw new SizeLimitExceededException(maxSizeLimit);
        }

        var entity = new DbFavoriteProject
        {
            ProjectId = projectId,
            UserId = requester.UserId,
            TenantId = requester.TenantId
        };

        _dbCtx.Add(entity);
        await _dbCtx.SaveChangesAsync();
    }

    public Task Remove(string projectId, IUserIdentity requester)
    {
        _dbCtx.Remove(new DbFavoriteProject
        {
            ProjectId = projectId,
            UserId = requester.UserId
        });

        return _dbCtx.SaveChangesAsync();
    }
}
