using Domain.Authentication;
using Microsoft.EntityFrameworkCore;
using Provider.Database.Context;
using Provider.Database.Projects.DbModels;

namespace Provider.Database.Projects;

internal class DbProjectSearch
{
    private readonly DatabaseContext _dbCtx;
    private readonly IUserIdentity _requester;

    public DbProjectSearch(DatabaseContext dbCtx, IUserIdentity requester)
    {
        _dbCtx = dbCtx;
        _requester = requester;
    }

    public IQueryable<DbProject> PreparedQuery()
    {
        var query = _dbCtx.Set<DbProject>()
            .Include(p => p.Avatar)
            .Include(p => p.Members)
            .OrderByDescending(p => p.CreatedAt);

        if (_requester.IsAdmin())
        {
            return query;
        }

        if (_requester.IsSupervisor())
        {
            return query.Where(p => p.TenantId == _requester.TenantId);
        }

        return query.Where(p =>
            p.Members.Any(pu => pu.UserId == _requester.UserId)
        );
    }
}
