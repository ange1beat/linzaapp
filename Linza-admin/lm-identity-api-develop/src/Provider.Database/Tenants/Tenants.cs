using Domain.Auth.Identity;
using Domain.Tenants;
using Microsoft.EntityFrameworkCore;
using Provider.Database.Context;

namespace Provider.Database.Tenants;

public class Tenants : ITenants
{
    private readonly IdentityDbContext _dbCtx;
    private readonly IAuthContext _authCtx;

    public Tenants(IdentityDbContext dbCtx, IAuthContext authCtx)
    {
        _dbCtx = dbCtx;
        _authCtx = authCtx;
    }

    public ITenantSearchQuery Search()
    {
        return new TenantSearchQuery(_dbCtx, _authCtx.LoggedInIdentity());
    }

    public async Task<ITenant> Tenant(string tenantId)
    {
        var dbTenant = await new DbTenantSearch(_dbCtx, _authCtx.LoggedInIdentity())
            .PreparedQuery()
            .SingleOrDefaultAsync();

        if (dbTenant is null)
        {
            throw new TenantNotFoundException(tenantId);
        }

        return new Tenant(dbTenant);
    }
}
