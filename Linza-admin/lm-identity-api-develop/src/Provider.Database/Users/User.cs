using Domain.Auth.Identity;
using Domain.Auth.Password;
using Domain.Files;
using Domain.Guid;
using Domain.Media;
using Domain.Users;
using Domain.Users.Exceptions;
using Domain.Users.Rules;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Provider.Database.Context;

namespace Provider.Database.Users;

internal sealed class User : IUser
{
    public string Id => _entity.Id;

    private readonly DbUser _entity;
    private readonly IdentityDbContext _dbCtx;
    private readonly IUserSettings _settings;
    private readonly IPasswordHasher _hasher;
    private readonly IFileStorage _files;
    private readonly IUserIdentity _requester;

    public User(
        DbUser entity,
        IdentityDbContext dbCtx,
        IUserSettings settings,
        IPasswordHasher hasher,
        IFileStorage files,
        IUserIdentity requester)
    {
        _entity = entity;
        _dbCtx = dbCtx;
        _settings = settings;
        _hasher = hasher;
        _files = files;
        _requester = requester;
    }

    public void Write(IMedia media)
    {
        media.Write("Id", _entity.Id);
        media.Write("TenantId", _entity.TenantId);
        media.Write("FirstName", _entity.FirstName);
        media.Write("LastName", _entity.LastName);
        media.Write("Email", _entity.Email);
        media.Write("PhoneNumber", _entity.PhoneNumber);
        media.Write("TelegramUsername", _entity.TelegramUsername);

        if (_entity.Avatar is not null)
        {
            media.Write(
                "AvatarUrl",
                _files.FileUri(_settings.AvatarScope, _entity.Avatar.FileName)
            );
        }

        media.Write("Roles", _entity.Roles.Select(r => r.Role).ToList());
        media.Write("LastLoginDate", _entity.LastLoginDate);
    }

    public bool IsPasswordMatch(string password)
    {
        return _hasher.Match(password, _entity.PasswordHash);
    }

    public async Task AttachAvatar(Stream content, string extension)
    {
        new UserCanUpdateAvatarRule(_entity.Id, _requester).Enforce();

        var prevAvatar = _entity.Avatar;
        var avatarId = new ShortGuid(Guid.NewGuid()).ToString();
        var avatar = new DbUserAvatar
        {
            Id = avatarId,
            FileName = $"{avatarId}.{extension.Trim().TrimStart('.')}",
            CreatedBy = _requester.UserId
        };
        _dbCtx.Add(avatar);

        await _dbCtx.SaveChangesAsync();

        await _files.Upload(_settings.AvatarScope, avatar.FileName, content);

        try
        {
            _entity.Avatar = avatar;
            _dbCtx.Update(_entity);

            await _dbCtx.SaveChangesAsync();
        }
        catch
        {
            await TryRemoveAvatar(avatar);

            throw;
        }

        if (prevAvatar is not null)
        {
            await TryRemoveAvatar(prevAvatar);
        }
    }

    public async Task RemoveAvatar()
    {
        new UserCanUpdateAvatarRule(_entity.Id, _requester).Enforce();

        if (_entity.Avatar is null)
        {
            return;
        }

        var avatar = _entity.Avatar;

        _entity.Avatar = null;
        _dbCtx.Update(_entity);

        await _dbCtx.SaveChangesAsync();

        await TryRemoveAvatar(avatar);
    }

    public Task ChangePassword(string password)
    {
        new UserCanChangePasswordRule(_entity.Id, _requester).Enforce();

        if (password.IsNullOrEmpty())
        {
            throw new ArgumentException("Password is required", nameof(password));
        }

        _entity.PasswordHash = _hasher.Hash(password);

        _dbCtx.Update(_entity);

        return _dbCtx.SaveChangesAsync();
    }

    public Task ChangeRoles(IEnumerable<Role> roles)
    {
        new UserCanChangeRolesRule(_entity.TenantId, _requester).Enforce();

        _entity.Roles = roles.Select(role => new DbUserRole
        {
            Role = role,
            UserId = _entity.Id
        }).ToList();

        _dbCtx.Update(_entity);

        return _dbCtx.SaveChangesAsync();
    }

    public async Task UpdateDetails(UserDetails details)
    {
        new UserCanUpdateDetailsRule(_entity.Id, _requester).Enforce();

        await ValidateDetails(details);

        _entity.FirstName = details.FirstName;
        _entity.LastName = details.LastName;
        _entity.Email = details.Email;
        _entity.PhoneNumber = details.PhoneNumber;
        _entity.TelegramUsername = details.TelegramUsername;

        _dbCtx.Update(_entity);

        await _dbCtx.SaveChangesAsync();
    }

    // ToDo: Method should be removed when there will be a background process
    //       to cleanup user's resources.
    internal async Task Delete()
    {
        _dbCtx.Remove(_entity);

        await _dbCtx.SaveChangesAsync();

        if (_entity.Avatar is not null)
        {
            await TryRemoveAvatar(_entity.Avatar);
        }
    }

    private async Task ValidateDetails(UserDetails details)
    {
        var emailNormalized = details.Email.ToUpper();
        var dbQuery = _dbCtx.Set<DbUser>()
            .Where(
                u => u.Id != _entity.Id &&
                    u.Email.ToUpper() == emailNormalized
            );

        if (details.PhoneNumber is not null)
        {
            dbQuery = dbQuery.Where(u => u.PhoneNumber == details.PhoneNumber);
        }

        var duplicates = await dbQuery
            .Select(u => new { u.Email, u.PhoneNumber })
            .ToListAsync();

        if (duplicates.Any(x => x.Email == details.Email))
        {
            throw new EmailConflictException(details.Email);
        }

        if (details.PhoneNumber is not null &&
            duplicates.Any(x => x.PhoneNumber == details.PhoneNumber))
        {
            throw new PhoneConflictException(details.PhoneNumber);
        }
    }

    // ToDo: add background process to cleanup 'orphan' avatars.
    // This method is not guarantee removal of the avatar
    // and must be replaced with a background process to cleanup the 'orphan' avatars.
    private async Task TryRemoveAvatar(DbUserAvatar avatar)
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
