using Domain.Auth.Factors;
using Domain.Auth.Tokens;
using Domain.Guid;
using Microsoft.EntityFrameworkCore;
using Newtonsoft.Json;
using Provider.Database.Context;
using Provider.Database.Tokens;

namespace Provider.Database.Auth.Tokens;

public class VerificationTokens : IVerificationTokens
{
    private readonly IdentityDbContext _dbCtx;
    private readonly IOneTimePass _oneTimePass;

    public VerificationTokens(IdentityDbContext dbCtx, IOneTimePass oneTimePass)
    {
        _dbCtx = dbCtx;
        _oneTimePass = oneTimePass;
    }

    public async Task<string> CreateToken(
        string userId,
        VerificationScope scope,
        TimeSpan lifeTime,
        IEnumerable<KeyValuePair<string, string>> properties)
    {
        var otpData = new VerificationTokenData
        {
            Scope = scope,
            Code = _oneTimePass.NextValue(),
            Properties = properties.ToDictionary()
        };

        var token = new DbUserToken
        {
            Id = new ShortGuid(Guid.NewGuid()).ToString(),
            Type = TokenType.Verification,
            UserId = userId,
            Data = JsonConvert.SerializeObject(otpData),
            ExpiresAt = DateTime.UtcNow.Add(lifeTime)
        };

        await using var transaction = _dbCtx.Transaction();

        await _dbCtx.Set<DbUserToken>()
            .Where(t => t.UserId == userId && t.Type == TokenType.Verification)
            .ExecuteDeleteAsync();

        _dbCtx.Add(token);

        await _dbCtx.SaveChangesAsync();

        await transaction.CommitAsync();

        return otpData.Code;
    }

    public async Task<IVerificationToken?> Token(string userId, VerificationScope scope)
    {
        var token = await _dbCtx.Set<DbUserToken>()
            .Where(t =>
                t.Type == TokenType.Verification &&
                t.UserId == userId &&
                t.ExpiresAt >= DateTime.UtcNow
            )
            .SingleOrDefaultAsync();

        if (token is null)
        {
            return null;
        }

        var tokenData = JsonConvert.DeserializeObject<VerificationTokenData>(token.Data!)!;

        if (tokenData.Scope != scope)
        {
            return null;
        }

        return new VerificationToken(token, tokenData, _dbCtx);
    }
}
