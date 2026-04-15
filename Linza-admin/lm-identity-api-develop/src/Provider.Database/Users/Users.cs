using Domain.Auth.Identity;
using Domain.Auth.Password;
using Domain.Files;
using Domain.Guid;
using Domain.Users;
using Domain.Users.Exceptions;
using Microsoft.EntityFrameworkCore;
using Provider.Database.Context;
using Provider.Database.Users.Invitations;

namespace Provider.Database.Users;

public class Users : IUsers
{
    private readonly IdentityDbContext _dbCtx;
    private readonly IUserSettings _settings;
    private readonly IAuthContext _authCtx;
    private readonly IPasswordHasher _hasher;
    private readonly IFileStorage _files;

    public Users(
        IdentityDbContext dbCtx,
        IUserSettings settings,
        IAuthContext authCtx,
        IPasswordHasher hasher,
        IFileStorage files)
    {
        _dbCtx = dbCtx;
        _settings = settings;
        _authCtx = authCtx;
        _hasher = hasher;
        _files = files;
        _authCtx = authCtx;
    }

    public IUserSearchQuery Search()
    {
        return new UserSearchQuery(
            _dbCtx, _settings, _hasher, _files, _authCtx.LoggedInIdentity()
        );
    }

    public async Task<IUser> User(string userId)
    {
        IEnumerable<IUser> users = await Search().WithIds(userId).Result();

        if (!users.Any())
        {
            throw new UserNotFoundException(userId);
        }

        return users.Single();
    }

    public async Task<IUser> NewUser(
        string invitationId,
        string firstName,
        string lastName,
        string password)
    {
        DbInvitation invitation = await Invitation(invitationId);

        var user = new DbUser
        {
            Id = new ShortGuid(Guid.NewGuid()).ToString(),
            TenantId = invitation.TenantId,
            FirstName = firstName,
            LastName = lastName,
            Email = invitation.UserEmail,
            PasswordHash = _hasher.Hash(password),
            Roles = new List<DbUserRole> { new() { Role = invitation.UserRole } }
        };

        await AddNewUser(user, invitation);

        return new User(
            user, _dbCtx, _settings, _hasher, _files, _authCtx.LoggedInIdentity()
        );
    }

    public async Task Remove(string userId)
    {
        IEnumerable<IUser> users = await Search().WithIds(userId).Result();

        if (!users.Any())
        {
            return;
        }

        await ((User)users.Single()).Delete();
    }

    private async Task<DbInvitation> Invitation(string invitationId)
    {
        var invitation = await _dbCtx.Set<DbInvitation>()
            .Where(inv =>
                inv.Id == invitationId &&
                inv.ExpiresAt >= DateTime.UtcNow
            )
            .SingleOrDefaultAsync();

        if (invitation is null)
        {
            throw new InvitationNotFoundException(invitationId);
        }

        return invitation;
    }

    private async Task AddNewUser(DbUser user, DbInvitation invitation)
    {
        _dbCtx.Add(user);
        _dbCtx.Remove(invitation);

        try
        {
            await _dbCtx.SaveChangesAsync();
        }
        // This exception can be thrown only when invitation was removed concurrently
        catch (DbUpdateConcurrencyException)
        {
            throw new InvitationNotFoundException(invitation.Id);
        }
        catch (DbUpdateException exc) when (
            _dbCtx.IsUniqueViolationError(exc, nameof(DbUser.Email)))
        {
            throw new EmailConflictException(user.Email);
        }
    }
}
