using Domain.Auth.Exceptions;
using Domain.Auth.Tokens;
using Microsoft.EntityFrameworkCore;
using Provider.Database.Context;
using Provider.Database.Tokens;

namespace Provider.Database.Auth.Tokens;

internal class VerificationToken : IVerificationToken
{
    public DateTime CreatedAt => _token.CreatedAt;

    public IReadOnlyDictionary<string, string> Properties =>
        _tokenData.Properties.AsReadOnly();

    private readonly DbUserToken _token;
    private readonly VerificationTokenData _tokenData;
    private readonly IdentityDbContext _dbCtx;

    public VerificationToken(
        DbUserToken token,
        VerificationTokenData tokenData,
        IdentityDbContext dbCtx)
    {
        _token = token;
        _tokenData = tokenData;
        _dbCtx = dbCtx;
    }

    public Task Use(string passcode)
    {
        if (_dbCtx.Entry(_token).State == EntityState.Deleted ||
            _tokenData.Code != passcode)
        {
            throw new AccessDeniedException();
        }

        _dbCtx.Remove(_token);
        try
        {
            return _dbCtx.SaveChangesAsync();
        }
        catch (DbUpdateException exc)
            when (exc is DbUpdateConcurrencyException)
        {
            // Someone else is already used this token concurrent
            throw new AccessDeniedException();
        }
    }
}
