using Domain.Auth.Identity;
using Provider.Database.Context;

namespace Provider.Database.Tenants;

internal sealed class DbTenantSearch
{
    private readonly IdentityDbContext _dbCtx;
    private readonly IUserIdentity _requester;

    public DbTenantSearch(IdentityDbContext dbCtx, IUserIdentity requester)
    {
        _dbCtx = dbCtx;
        _requester = requester;
    }

    public IQueryable<DbTenant> PreparedQuery()
    {
        var query = _dbCtx.Set<DbTenant>().OrderBy(t => t.Name);

        if (_requester.IsInRole(Role.Admin))
        {
            return query;
        }

        return query.Where(t => t.Id == _requester.TenantId);
    }
}
