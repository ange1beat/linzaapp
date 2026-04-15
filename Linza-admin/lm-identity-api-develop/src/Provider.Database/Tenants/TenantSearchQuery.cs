using Domain.Auth.Identity;
using Domain.Search;
using Domain.Tenants;
using Microsoft.EntityFrameworkCore;
using Provider.Database.Context;

namespace Provider.Database.Tenants;

internal sealed class TenantSearchQuery : ITenantSearchQuery
{
    private readonly IdentityDbContext _dbCtx;
    private readonly IUserIdentity _requester;
    private readonly Context _context;

    public TenantSearchQuery(IdentityDbContext dbCtx, IUserIdentity requester)
        : this(dbCtx, requester, new Context())
    {
    }

    private TenantSearchQuery(IdentityDbContext dbCtx, IUserIdentity requester, Context context)
    {
        _dbCtx = dbCtx;
        _requester = requester;
        _context = context;
    }

    public ITenantSearchQuery WithTerm(string searchTerm)
    {
        var context = _context with { SearchTerm = searchTerm.Trim() };

        return new TenantSearchQuery(_dbCtx, _requester, context);
    }

    public ITenantSearchQuery WithPagination(Pagination pagination)
    {
        var context = _context with { Pagination = pagination };

        return new TenantSearchQuery(_dbCtx, _requester, context);
    }

    public async Task<IReadOnlyCollection<ITenant>> Result()
    {
        var preparedQuery = PaginatedQuery(FilteredQuery(Query()));

        var queryResult = await preparedQuery.ToListAsync();

        return queryResult.Select(t => new Tenant(t)).ToList();
    }

    public Task<int> Total()
    {
        var preparedQuery = FilteredQuery(Query());

        return preparedQuery.CountAsync();
    }

    private sealed record Context(string SearchTerm, Pagination Pagination)
    {
        public Context() : this(string.Empty, new Pagination())
        {
        }
    }

    private IQueryable<DbTenant> Query()
    {
        return new DbTenantSearch(_dbCtx, _requester).PreparedQuery();
    }

    private IQueryable<DbTenant> FilteredQuery(IQueryable<DbTenant> query)
    {
        if (!string.IsNullOrEmpty(_context.SearchTerm))
        {
            query = query.Where(t => EF.Functions.Like(t.Name, _context.SearchTerm));
        }

        return query;
    }

    private IQueryable<DbTenant> PaginatedQuery(IQueryable<DbTenant> query)
    {
        var (pageNumber, pageSize) = _context.Pagination;

        return query
            .Skip((pageNumber - 1) * pageSize)
            .Take(pageSize);
    }
}
