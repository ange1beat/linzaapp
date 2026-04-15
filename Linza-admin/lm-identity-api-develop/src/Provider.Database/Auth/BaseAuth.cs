using Domain.Auth;
using Domain.Auth.Exceptions;
using Domain.Auth.Factors;
using Domain.Auth.Password;
using Domain.Guid;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Newtonsoft.Json;
using Provider.Database.Auth.Tokens;
using Provider.Database.Context;
using Provider.Database.Tokens;
using Provider.Database.Users;

namespace Provider.Database.Auth;

public class BaseAuth : IBaseAuth
{
    private readonly IdentityDbContext _dbCtx;
    private readonly IAuthSettings _settings;
    private readonly IPasswordHasher _passwordHasher;

    public BaseAuth(
        IdentityDbContext dbCtx,
        IAuthSettings settings,
        IPasswordHasher passwordHasher)
    {
        _dbCtx = dbCtx;
        _settings = settings;
        _passwordHasher = passwordHasher;
    }

    public async Task<IAuthState> Authenticate(string login, string password)
    {
        if (login.IsNullOrEmpty() || password.IsNullOrEmpty())
        {
            throw new UnauthorizedException();
        }

        DbUser user = await User(login);

        await Verify(user, password);

        user.AccessFailedCount = 0;
        user.LockoutEndDate = null;

        var stateToken = NewStateToken(user);

        await using var transaction = _dbCtx.Transaction();

        // Remove all pending authentication sessions of user
        await _dbCtx.Set<DbUserToken>()
            .Where(t =>
                t.UserId == user.Id &&
                t.Type == TokenType.Authentication
            )
            .ExecuteDeleteAsync();

        _dbCtx.Update(user);
        _dbCtx.Add(stateToken);

        await _dbCtx.SaveChangesAsync();

        await transaction.CommitAsync();

        return new AuthState(stateToken);
    }

    private async Task<DbUser> User(string login)
    {
        var user = await _dbCtx.Set<DbUser>()
            .Where(u =>
                u.Email.ToUpper() == login.ToUpper() ||
                (
                    u.PhoneNumber != null &&
                    u.PhoneNumber == login
                )
            )
            .SingleOrDefaultAsync();

        if (user is null)
        {
            throw new UnauthorizedException();
        }

        return user;
    }

    private async Task Verify(DbUser user, string password)
    {
        var currentTimeUtc = DateTime.UtcNow;

        var isAccountLocked =
            user.LockoutEndDate is not null &&
            user.LockoutEndDate >= currentTimeUtc;

        int accessFailedCount = user.AccessFailedCount;

        // Resets count of failed access attempts
        //     if enough time has gone after the last failed attempt
        if (!isAccountLocked &&
            user.LastFailedAccessDate + _settings.LockoutDuration <= currentTimeUtc)
        {
            accessFailedCount = 0;
        }

        if (!_passwordHasher.Match(password, user.PasswordHash))
        {
            // Check if account should be locked for a time
            if (!isAccountLocked)
            {
                accessFailedCount++;
                if (accessFailedCount >= _settings.MaxFailedAccessAttempts)
                {
                    user.LockoutEndDate = currentTimeUtc.Add(_settings.LockoutDuration);
                }
            }

            user.AccessFailedCount = accessFailedCount;
            user.LastFailedAccessDate = currentTimeUtc;

            _dbCtx.Update(user);

            await _dbCtx.SaveChangesAsync();

            throw new UnauthorizedException();
        }

        // Account lockout check must follow after password verification
        //     to avoid enumeration attack to accounts
        if (isAccountLocked)
        {
            throw new AccountLockedException(user.LockoutEndDate!.Value);
        }
    }

    private DbUserToken NewStateToken(DbUser user)
    {
        return new DbUserToken
        {
            Id = new ShortGuid(System.Guid.NewGuid()).ToString(),
            Type = TokenType.Authentication,
            UserId = user.Id,
            User = user,
            Data = JsonConvert.SerializeObject(new AuthTokenData
            {
                Factors = new List<FactorType> { FactorType.Otp },
                FactorsRequiredNumber = 1
            }),
            ExpiresAt = DateTime.UtcNow.Add(_settings.StateTokenTtl)
        };
    }
}
