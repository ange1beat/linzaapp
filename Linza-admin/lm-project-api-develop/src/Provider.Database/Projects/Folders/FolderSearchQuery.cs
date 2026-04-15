using Domain.Authentication;
using Domain.Projects.Folders;
using Domain.Search;
using Microsoft.EntityFrameworkCore;
using Provider.Database.Context;
using Provider.Database.Projects.DbModels;

namespace Provider.Database.Projects.Folders;

public class FolderSearchQuery : IFolderSearchQuery
{
    private readonly string _projectId;
    private readonly DatabaseContext _dbCtx;
    private readonly IUserIdentity _user;
    private readonly string _name;
    private readonly Pagination _pagination;

    public FolderSearchQuery(
        string projectId,
        DatabaseContext dbCtx,
        IUserIdentity user
    ) : this(
        projectId,
        dbCtx, user,
        string.Empty,
        new Pagination())
    {
    }

    private FolderSearchQuery(
        string projectId,
        DatabaseContext dbCtx,
        IUserIdentity user,
        string name,
        Pagination pagination)
    {
        _projectId = projectId;
        _dbCtx = dbCtx;
        _user = user;
        _name = name;
        _pagination = pagination;
    }

    public IFolderSearchQuery WithName(string name)
    {
        return new FolderSearchQuery(_projectId, _dbCtx, _user, name, _pagination);
    }

    public IFolderSearchQuery WithPagination(Pagination pagination)
    {
        return new FolderSearchQuery(_projectId, _dbCtx, _user, _name, pagination);
    }

    public async Task<IReadOnlyCollection<IFolder>> Result()
    {
        IQueryable<DbFolder> query = PaginatedQuery(FilteredQuery(Query()));

        IEnumerable<DbFolder> entities = await query.ToListAsync();

        return entities.Select(x => new Folder(x, _dbCtx, _user)).ToList();
    }

    public Task<int> Total()
    {
        IQueryable<DbFolder> query = FilteredQuery(Query());

        return query.CountAsync();
    }

    private IQueryable<DbFolder> Query()
    {
        return _dbCtx.Set<DbFolder>().OrderBy(p => p.Name);
    }

    private IQueryable<DbFolder> FilteredQuery(
        IQueryable<DbFolder> query)
    {
        query = query.Where(f => f.ProjectId == _projectId);

        if (_name.Length != 0)
        {
            query = query.Where(f => EF.Functions.Like(
                f.Name.ToUpper(),
                $"%{_name.ToUpper()}%"
            ));
        }

        return query;
    }

    private IQueryable<DbFolder> PaginatedQuery(
        IQueryable<DbFolder> query)
    {
        var (pageNumber, pageSize) = _pagination;

        return query
            .Skip((pageNumber - 1) * pageSize)
            .Take(pageSize);
    }
}
