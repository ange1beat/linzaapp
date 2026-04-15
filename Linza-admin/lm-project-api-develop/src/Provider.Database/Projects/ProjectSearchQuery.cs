using Domain.Authentication;
using Domain.Files;
using Domain.Projects;
using Domain.Search;
using Microsoft.EntityFrameworkCore;
using Provider.Database.Context;
using Provider.Database.Projects.DbModels;

namespace Provider.Database.Projects;

internal sealed class ProjectSearchQuery : IProjectSearchQuery
{
    private readonly DatabaseContext _dbCtx;
    private readonly IProjectSettings _settings;
    private readonly IFileStorage _files;
    private readonly IUserIdentity _user;
    private readonly Filters _filters;
    private readonly Pagination _pagination;

    public ProjectSearchQuery(
        DatabaseContext dbCtx,
        IProjectSettings settings,
        IFileStorage files,
        IUserIdentity user
    ) : this(
        dbCtx,
        settings,
        files,
        user,
        new Filters(),
        new Pagination())
    {
    }

    private ProjectSearchQuery(
        DatabaseContext dbCtx,
        IProjectSettings settings,
        IFileStorage files,
        IUserIdentity user,
        Filters filters,
        Pagination pagination)
    {
        _dbCtx = dbCtx;
        _settings = settings;
        _files = files;
        _user = user;
        _filters = filters;
        _pagination = pagination;
    }

    public IProjectSearchQuery WithName(string name)
    {
        var filters = _filters with { Name = name };

        return new ProjectSearchQuery(
            _dbCtx, _settings, _files, _user, filters, _pagination
        );
    }

    public IProjectSearchQuery WithIds(params string[] ids)
    {
        var filters = _filters with { ProjectIds = ids };

        return new ProjectSearchQuery(
            _dbCtx, _settings, _files, _user, filters, _pagination
        );
    }

    public IProjectSearchQuery WithTenant(string tenantId)
    {
        var filters = _filters with { TenantId = tenantId };

        return new ProjectSearchQuery(
            _dbCtx, _settings, _files, _user, filters, _pagination
        );
    }

    public IProjectSearchQuery WithPagination(Pagination pagination)
    {
        return new ProjectSearchQuery(
            _dbCtx, _settings, _files, _user, _filters, pagination
        );
    }

    public Task<bool> Any()
    {
        IQueryable<DbProject> query = PaginatedQuery(FilteredQuery(Query()));

        return query.AnyAsync();
    }

    public async Task<IReadOnlyList<IProject>> Projects()
    {
        IQueryable<DbProject> query = PaginatedQuery(FilteredQuery(Query()));

        IEnumerable<DbProject> result = await query.ToListAsync();

        return result
            .Select(x => new Project(x, _dbCtx, _settings, _files, _user))
            .ToList();
    }

    public Task<int> Total()
    {
        return FilteredQuery(Query()).CountAsync();
    }

    private sealed record Filters(
        string Name,
        string TenantId,
        IEnumerable<string> ProjectIds)
    {
        public Filters() : this(
            string.Empty, string.Empty, Array.Empty<string>())
        {
        }
    }

    private IQueryable<DbProject> Query()
    {
        return new DbProjectSearch(_dbCtx, _user).PreparedQuery();
    }

    private IQueryable<DbProject> FilteredQuery(IQueryable<DbProject> query)
    {
        if (!string.IsNullOrEmpty(_filters.Name))
        {
            query = query.Where(p => EF.Functions.Like(
                p.Name.ToUpper(),
                $"%{_filters.Name.ToUpper()}%"
            ));
        }

        if (!string.IsNullOrEmpty(_filters.TenantId))
        {
            query = query.Where(p => p.TenantId == _filters.TenantId);
        }

        if (_filters.ProjectIds.Any())
        {
            query = query.Where(p => _filters.ProjectIds.Contains(p.Id));
        }

        return query;
    }

    private IQueryable<DbProject> PaginatedQuery(IQueryable<DbProject> query)
    {
        var (pageNumber, pageSize) = _pagination;

        return query
            .Skip((pageNumber - 1) * pageSize)
            .Take(pageSize);
    }
}
