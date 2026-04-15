using Domain.Auth;
using Domain.Auth.Exceptions;
using Domain.Auth.Identity;
using Domain.Auth.Tokens;
using Domain.Auth.Tokens.Claims;
using Domain.Projects;
using Microsoft.EntityFrameworkCore;
using Newtonsoft.Json;
using Provider.Database.Context;
using Provider.Database.Tokens;
using Provider.Database.Users;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Security.Cryptography;

namespace Provider.Database.Auth.Tokens;

public class AuthTokens : IAuthTokens
{
    private readonly IdentityDbContext _dbCtx;
    private readonly IAuthSettings _settings;
    private readonly IProjects _projects;

    public AuthTokens(IdentityDbContext dbCtx, IAuthSettings settings, IProjects projects)
    {
        _dbCtx = dbCtx;
        _settings = settings;
        _projects = projects;
    }

    public async Task<AuthToken> NewToken(string stateToken)
    {
        DbUserToken authStateToken = await UserToken(stateToken, TokenType.Authentication);

        var authState = JsonConvert.DeserializeObject<AuthTokenData>(authStateToken.Data!)!;

        if (!authState.IsCompleted())
        {
            throw new UnauthorizedException();
        }

        JwtSecurityToken accessToken = await AccessToken(authStateToken.User);

        DbUserToken refreshToken = RefreshToken(
            authStateToken.UserId,
            DateTime.UtcNow.Add(_settings.RefreshTokenTtl)
        );

        var authToken = new AuthToken(
            new JwtSecurityTokenHandler().WriteToken(accessToken),
            refreshToken.Id,
            accessToken.ValidTo,
            refreshToken.ExpiresAt
        );

        authStateToken.User.LastLoginDate = DateTime.UtcNow;

        try
        {
            _dbCtx.Add(refreshToken);
            _dbCtx.Update(authStateToken.User);
            _dbCtx.Remove(authStateToken);

            await _dbCtx.SaveChangesAsync();
        }
        catch (DbUpdateConcurrencyException)
        {
            /* This case occurs when multiple concurrent threads try to use the same State Token
               but each State Token can be used only once.
               Only one thread gets new Auth Token while others get error
               because the State Token was already used. */
            throw new UnauthorizedAccessException();
        }

        // ToDo: Move cleanup to background process
        // Cleanup expired refresh tokens of user
        await _dbCtx.Set<DbUserToken>()
            .Where(t =>
                t.UserId == authStateToken.UserId &&
                t.Type == TokenType.Refresh &&
                t.ExpiresAt < DateTime.UtcNow
            )
            .ExecuteDeleteAsync();

        return authToken;
    }

    public async Task<AuthToken> RefreshedToken(string refreshToken)
    {
        DbUserToken currentRefreshToken = await UserToken(refreshToken, TokenType.Refresh);

        JwtSecurityToken accessToken = await AccessToken(currentRefreshToken.User);

        DbUserToken newRefreshToken = RefreshToken(
            currentRefreshToken.UserId,
            currentRefreshToken.ExpiresAt
        );

        var authToken = new AuthToken(
            new JwtSecurityTokenHandler().WriteToken(accessToken),
            newRefreshToken.Id,
            accessToken.ValidTo,
            newRefreshToken.ExpiresAt
        );

        try
        {
            _dbCtx.Add(newRefreshToken);
            _dbCtx.Remove(currentRefreshToken);

            await _dbCtx.SaveChangesAsync();
        }
        catch (DbUpdateConcurrencyException)
        {
            /* This case occurs when multiple concurrent threads try to use the same Refresh Token
               but each Refresh Token can be used only once.
               Only one thread gets refreshed Auth Token while others get error
               because the Refresh Token was already used. */
            throw new UnauthorizedAccessException();
        }

        return authToken;
    }

    public Task RevokeRefreshToken(string refreshToken)
    {
        return _dbCtx.Set<DbUserToken>()
            .Where(t =>
                t.Id == refreshToken &&
                t.Type == TokenType.Refresh
            )
            .ExecuteDeleteAsync();
    }

    private async Task<DbUserToken> UserToken(string tokenId, TokenType type)
    {
        var dbToken = await _dbCtx.Set<DbUserToken>()
            .Include(t => t.User)
            .ThenInclude(u => u.Roles)
            .Where(t =>
                t.Id == tokenId &&
                t.Type == type &&
                t.ExpiresAt >= DateTime.UtcNow
            )
            .SingleOrDefaultAsync();

        if (dbToken is null)
        {
            throw new UnauthorizedException();
        }

        return dbToken;
    }

    private async Task<JwtSecurityToken> AccessToken(DbUser user)
    {
        var claims = new List<Claim>
        {
            new IdClaim(user.Id),
            new TenantClaim(user.TenantId),
            new RolesClaim(user.Roles.Select(r => r.Role))
        };

        var userRoles = user.Roles.Select(r => r.Role).ToList();
        if (userRoles.Count == 1 && userRoles.Single() is Role.User)
        {
            claims.Add(new ProjectsClaim(
                await _projects.ProjectIds(user.Id)
            ));
        }

        IJwtSettings settings = _settings.AccessToken;

        return new JwtSecurityToken(
            issuer: settings.Issuer,
            audience: settings.Audience,
            claims: claims,
            expires: DateTime.UtcNow.Add(settings.ExpirationTime),
            signingCredentials: settings.SigningCredentials()
        );
    }

    private static DbUserToken RefreshToken(string userId, DateTime expiresAt)
    {
        using var rng = RandomNumberGenerator.Create();

        var tokenId = new byte[32];
        rng.GetBytes(tokenId);

        return new DbUserToken
        {
            Id = Convert.ToBase64String(tokenId),
            Type = TokenType.Refresh,
            UserId = userId,
            ExpiresAt = expiresAt
        };
    }
}
