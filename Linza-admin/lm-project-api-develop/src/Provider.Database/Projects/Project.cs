using Domain.Authentication;
using Domain.Exceptions;
using Domain.Files;
using Domain.Media;
using Domain.Projects;
using Domain.Projects.Folders;
using Domain.Projects.Rules;
using Microsoft.EntityFrameworkCore;
using Provider.Database.Context;
using Provider.Database.Guid;
using Provider.Database.Projects.DbModels;
using Provider.Database.Projects.Folders;

namespace Provider.Database.Projects;

internal sealed class Project : IProject
{
    public string Id => _entity.Id;

    private readonly DbProject _entity;
    private readonly DatabaseContext _dbCtx;
    private readonly IProjectSettings _settings;
    private readonly IFileStorage _files;
    private readonly IUserIdentity _user;

    public Project(
        DbProject entity,
        DatabaseContext dbCtx,
        IProjectSettings settings,
        IFileStorage files,
        IUserIdentity user)
    {
        _entity = entity;
        _dbCtx = dbCtx;
        _settings = settings;
        _files = files;
        _user = user;
    }

    public void Write(IMedia media)
    {
        media.Write("Id", _entity.Id);
        media.Write("Name", _entity.Name);
        media.Write("TenantId", _entity.TenantId);
        media.Write("CreatedBy", _entity.CreatedBy);
        media.Write("CreatedAt", _entity.CreatedAt);

        if (_entity.Avatar is not null)
        {
            Uri avatarUrl = _files.FileUri(
                _settings.AvatarScope,
                _entity.Avatar.FileName
            );
            media.Write("AvatarUrl", avatarUrl);
        }
    }

    public IProjectFolders Folders()
    {
        return new ProjectFolders(_entity.Id, _dbCtx, _user);
    }

    public IProjectMembers Members()
    {
        new UserCanAccessProjectMembersRule(_user).Enforce();

        return new ProjectMembers(_entity, _dbCtx, _user);
    }

    public async Task Rename(string name)
    {
        new UserCanUpdateProjectRule(_user).Enforce();

        if (string.IsNullOrEmpty(name))
        {
            throw new ArgumentException(
                "Name must not be NULL or empty",
                nameof(name)
            );
        }

        if (_entity.Name.Equals(name, StringComparison.InvariantCultureIgnoreCase))
        {
            return;
        }

        if (await _dbCtx.Set<DbProject>().AnyAsync(p =>
                p.TenantId == _entity.TenantId &&
                p.Id != _entity.Id &&
                p.Name.ToUpper() == name.ToUpper()))
        {
            throw new ConstraintException("Project name must be unique!");
        }

        _entity.Name = name;

        _dbCtx.Update(_entity);

        try
        {
            await _dbCtx.SaveChangesAsync();
        }
        catch (DbUpdateConcurrencyException exc)
        {
            throw new ConcurrencyException(exc);
        }
    }

    public async Task AttachAvatar(Stream content, string extension)
    {
        new UserCanUpdateProjectRule(_user).Enforce();

        var avatarId = new ShortGuid(System.Guid.NewGuid()).ToString();

        var avatar = new DbProjectAvatar
        {
            Id = avatarId,
            FileName = $"{avatarId}.{extension.Trim().TrimStart('.')}",
            CreatedBy = _user.UserId
        };
        _dbCtx.Add(avatar);

        await _dbCtx.SaveChangesAsync();

        await _files.Upload(_settings.AvatarScope, avatar.FileName, content);

        var prevAvatar = _entity.Avatar;

        _entity.Avatar = avatar;
        _dbCtx.Update(_entity);

        try
        {
            await _dbCtx.SaveChangesAsync();
        }
        catch (Exception)
        {
            await TryRemoveAvatarFile(avatar);

            throw;
        }

        if (prevAvatar is not null)
        {
            await TryRemoveAvatarFile(prevAvatar);
        }
    }

    public async Task RemoveAvatar()
    {
        new UserCanUpdateProjectRule(_user).Enforce();

        if (_entity.Avatar is null)
        {
            return;
        }

        var avatar = _entity.Avatar;

        _entity.Avatar = null;
        _dbCtx.Update(_entity);

        await _dbCtx.SaveChangesAsync();

        await TryRemoveAvatarFile(avatar);
    }

    internal async Task Delete()
    {
        _dbCtx.Remove(_entity);

        await _dbCtx.SaveChangesAsync();

        if (_entity.Avatar is not null)
        {
            await TryRemoveAvatarFile(_entity.Avatar);
        }
    }

    // ToDo: add background process to cleanup 'dangling' avatars.
    // This method is not guarantee removal of the avatar
    // and must be replaced with a background process to cleanup the 'orphan' avatars.
    private async Task TryRemoveAvatarFile(DbProjectAvatar avatar)
    {
        try
        {
            await _files.Remove(_settings.AvatarScope, avatar.FileName);

            _dbCtx.Remove(avatar);

            await _dbCtx.SaveChangesAsync();
        }
        catch (Exception)
        {
            // ignored
        }
    }
}
