using Domain.Authentication;
using Domain.Media;
using Domain.Projects.Exceptions;
using Domain.Projects.Folders;
using Microsoft.EntityFrameworkCore;
using Provider.Database.Context;
using Provider.Database.Projects.DbModels;

namespace Provider.Database.Projects.Folders;

internal sealed class Folder : IFolder
{
    private readonly DbFolder _entity;
    private readonly DatabaseContext _dbCtx;
    private readonly IUserIdentity _user;

    public Folder(
        DbFolder entity,
        DatabaseContext dbCtx,
        IUserIdentity user)
    {
        _entity = entity;
        _dbCtx = dbCtx;
        _user = user;
    }

    public void Write(IMedia media)
    {
        media.Write("Id", _entity.Id);
        media.Write("Name", _entity.Name);
    }

    public async Task Rename(string name)
    {
        if (string.IsNullOrEmpty(name))
        {
            throw new ArgumentException(
                "Name must not be NULL or empty",
                nameof(name)
            );
        }

        if (await _dbCtx.Set<DbFolder>().AnyAsync(f =>
                f.ProjectId == _entity.ProjectId &&
                f.Id != _entity.Id &&
                f.Name.ToUpper() == name.ToUpper()))
        {
            throw new FolderNameConflictException();
        }

        _entity.Name = name;
        _entity.UpdatedBy = _user.UserId;

        await _dbCtx.SaveChangesAsync();
    }
}
