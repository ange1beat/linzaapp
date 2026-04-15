using Domain.Auth.Exceptions;
using Domain.Auth.Password;
using Domain.Auth.Recovery;
using Domain.Auth.Tokens;
using Domain.Guid;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Provider.Database.Context;
using Provider.Database.Tokens;
using Provider.Database.Users;

namespace Provider.Database.Auth.Recovery;

public class PasswordRecovery : IPasswordRecovery
{
    private const string RecipientPropKey = "Recipient";

    private readonly IdentityDbContext _dbCtx;
    private readonly IRecoverySettings _settings;
    private readonly IVerificationTokens _verificationTokens;
    private readonly IPasswordHasher _passwordHasher;

    public PasswordRecovery(
        IdentityDbContext dbCtx,
        IRecoverySettings settings,
        IVerificationTokens verificationTokens,
        IPasswordHasher passwordHasher)
    {
        _dbCtx = dbCtx;
        _settings = settings;
        _verificationTokens = verificationTokens;
        _passwordHasher = passwordHasher;
    }

    public async Task<string> RecoveryToken(string login, string recoveryCode)
    {
        if (login.IsNullOrEmpty() || recoveryCode.IsNullOrEmpty())
        {
            throw new AccessDeniedException();
        }

        DbUser user = await User(login);

        await VerifyRecoveryCode(user, recoveryCode);

        var recoveryToken = new DbUserToken
        {
            Id = new ShortGuid(Guid.NewGuid()).ToString(),
            Type = TokenType.PasswordReset,
            UserId = user.Id,
            User = user,
            ExpiresAt = DateTime.UtcNow.Add(_settings.RecoveryTokenTtl)
        };

        _dbCtx.Add(recoveryToken);

        await _dbCtx.SaveChangesAsync();

        return recoveryToken.Id;
    }

    public async Task ResetPassword(string recoveryToken, string newPassword)
    {
        if (newPassword.IsNullOrEmpty())
        {
            throw new ArgumentException("Invalid password", nameof(newPassword));
        }

        DbUserToken token = await RecoveryToken(recoveryToken);
        DbUser user = token.User;

        user.PasswordHash = _passwordHasher.Hash(newPassword);

        _dbCtx.Update(user);
        _dbCtx.Remove(token);

        await _dbCtx.SaveChangesAsync();
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
            throw new AccessDeniedException();
        }

        return user;
    }

    private async Task VerifyRecoveryCode(DbUser user, string recoveryCode)
    {
        IVerificationToken? otpToken = await _verificationTokens.Token(
            user.Id,
            VerificationScope.PasswordRecovery
        );

        if (otpToken is null)
        {
            throw new UnauthorizedException();
        }

        otpToken.Properties.TryGetValue(RecipientPropKey, out var recipient);
        if (recipient != user.Email && recipient != user.PhoneNumber)
        {
            throw new UnauthorizedException();
        }

        await otpToken.Use(recoveryCode);
    }

    private async Task<DbUserToken> RecoveryToken(string id)
    {
        var dbStateToken = await _dbCtx.Set<DbUserToken>()
            .Include(t => t.User)
            .Where(t =>
                t.Id == id &&
                t.Type == TokenType.PasswordReset &&
                t.ExpiresAt >= DateTime.UtcNow
            )
            .SingleOrDefaultAsync();

        if (dbStateToken is null)
        {
            throw new AccessDeniedException();
        }

        return dbStateToken;
    }
}
