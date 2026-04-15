using Domain.Authentication;
using Domain.Projects.Exceptions;
using Domain.Projects.Folders;
using Microsoft.EntityFrameworkCore;
using Provider.Database.Context;
using Provider.Database.Guid;
using Provider.Database.Projects.DbModels;

namespace Provider.Database.Projects.Folders;

public class ProjectFolders : IProjectFolders
{
    private readonly string _projectId;
    private readonly DatabaseContext _dbCtx;
    private readonly IUserIdentity _user;

    public ProjectFolders(string projectId, DatabaseContext dbCtx, IUserIdentity user)
    {
        _projectId = projectId;
        _dbCtx = dbCtx;
        _user = user;
    }

    public IFolderSearchQuery SearchQuery()
    {
        return new FolderSearchQuery(_projectId, _dbCtx, _user);
    }

    public async Task<IFolder> Folder(string id)
    {
        var entity = await _dbCtx.Set<DbFolder>().SingleOrDefaultAsync(f =>
            f.Id == id && f.ProjectId == _projectId
        );

        if (entity is null)
        {
            throw new FolderNotFoundException(id);
        }

        return new Folder(entity, _dbCtx, _user);
    }

    public async Task<IFolder> NewFolder(string name)
    {
        if (string.IsNullOrEmpty(name))
        {
            throw new ArgumentException(
                "Name must not be NULL or empty",
                nameof(name)
            );
        }

        if (await _dbCtx.Set<DbFolder>().AnyAsync(f =>
                f.ProjectId == _projectId &&
                f.Name.ToUpper() == name.ToUpper()))
        {
            throw new FolderNameConflictException();
        }

        var entity = new DbFolder
        {
            Id = new ShortGuid(System.Guid.NewGuid()).ToString(),
            Name = name,
            ProjectId = _projectId,
            CreatedBy = _user.UserId,
            UpdatedBy = _user.UserId
        };

        _dbCtx.Add(entity);

        await _dbCtx.SaveChangesAsync();

        return new Folder(entity, _dbCtx, _user);
    }

    public async Task Remove(string id)
    {
        await _dbCtx.Set<DbFolder>()
            .Where(f => f.Id == id)
            .ExecuteDeleteAsync();
    }
}
