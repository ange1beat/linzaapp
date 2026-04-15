using Domain.Auth.Identity;
using Domain.Auth.Password;
using Domain.Files;
using Domain.Search;
using Domain.Users;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Provider.Database.Context;

namespace Provider.Database.Users;

internal sealed class UserSearchQuery : IUserSearchQuery
{
    private readonly IdentityDbContext _dbCtx;
    private readonly IUserSettings _settings;
    private readonly IPasswordHasher _hasher;
    private readonly IFileStorage _files;
    private readonly IUserIdentity _requester;
    private readonly Filters _filters;
    private readonly Pagination _pagination;

    public UserSearchQuery(
        IdentityDbContext dbCtx,
        IUserSettings settings,
        IPasswordHasher hasher,
        IFileStorage files,
        IUserIdentity requester
    ) : this(
        dbCtx,
        settings,
        hasher,
        files,
        requester,
        new Filters(),
        new Pagination())
    {
    }

    private UserSearchQuery(
        IdentityDbContext dbCtx,
        IUserSettings settings,
        IPasswordHasher hasher,
        IFileStorage files,
        IUserIdentity requester,
        Filters filters,
        Pagination pagination)
    {
        _dbCtx = dbCtx;
        _settings = settings;
        _hasher = hasher;
        _files = files;
        _requester = requester;
        _filters = filters;
        _pagination = pagination;
    }

    public IUserSearchQuery WithIds(params string[] ids)
    {
        return WithUpdatedFilters(_filters with { IncludeIds = ids });
    }

    public IUserSearchQuery WithoutIds(params string[] ids)
    {
        return WithUpdatedFilters(_filters with { ExcludeIds = ids });
    }

    public IUserSearchQuery WithTenant(string tenantId)
    {
        if (tenantId.IsNullOrEmpty())
        {
            throw new ArgumentException("Invalid tenant ID", nameof(tenantId));
        }

        return WithUpdatedFilters(_filters with { TenantId = tenantId });
    }

    public IUserSearchQuery WithSearchTerm(string searchTerm)
    {
        if (searchTerm.IsNullOrEmpty())
        {
            throw new ArgumentException("Invalid search term", nameof(searchTerm));
        }

        return WithUpdatedFilters(_filters with { SearchTerm = searchTerm });
    }

    public IUserSearchQuery WithEmail(string email)
    {
        if (email.IsNullOrEmpty())
        {
            throw new ArgumentException("Invalid email", nameof(email));
        }

        return WithUpdatedFilters(_filters with { Email = email });
    }

    public IUserSearchQuery WithPhone(string phoneNumber)
    {
        if (phoneNumber.IsNullOrEmpty())
        {
            throw new ArgumentException("Invalid phone number", nameof(phoneNumber));
        }

        return WithUpdatedFilters(_filters with { PhoneNumber = phoneNumber });
    }

    public IUserSearchQuery WithPagination(Pagination pagination)
    {
        return new UserSearchQuery(
            _dbCtx, _settings, _hasher, _files, _requester, _filters, pagination
        );
    }

    public Task<bool> Any()
    {
        IQueryable<DbUser> query = FilteredQuery(Query());

        return query.AnyAsync();
    }

    public async Task<IReadOnlyCollection<IUser>> Result()
    {
        IQueryable<DbUser> query = PaginatedQuery(FilteredQuery(Query()));

        IEnumerable<DbUser> result = await query.ToListAsync();

        return result
            .Select(x => new User(x, _dbCtx, _settings, _hasher, _files, _requester))
            .ToList();
    }

    public Task<int> Total()
    {
        return FilteredQuery(Query()).CountAsync();
    }

    private sealed record Filters(
        string SearchTerm,
        string TenantId,
        string Email,
        string PhoneNumber,
        IEnumerable<string> IncludeIds,
        IEnumerable<string> ExcludeIds,
        IEnumerable<Role> Roles)
    {
        public Filters() : this(
            string.Empty,
            string.Empty,
            string.Empty,
            string.Empty,
            Array.Empty<string>(),
            Array.Empty<string>(),
            Array.Empty<Role>())
        {
        }
    }

    private IUserSearchQuery WithUpdatedFilters(Filters filters)
    {
        return new UserSearchQuery(
            _dbCtx, _settings, _hasher, _files, _requester, filters, _pagination
        );
    }

    private IQueryable<DbUser> Query()
    {
        IQueryable<DbUser> query = _dbCtx.Set<DbUser>()
            .Include(u => u.Roles)
            .Include(u => u.Avatar)
            .OrderBy(u => u.FirstName)
            .ThenBy(u => u.LastName);

        if (_requester.IsInRole(Role.Admin))
        {
            return query;
        }

        if (_requester.IsInRole(Role.Supervisor))
        {
            return query.Where(u => u.TenantId == _requester.TenantId);
        }

        return query.Where(u => u.Id == _requester.UserId);
    }

    private IQueryable<DbUser> FilteredQuery(IQueryable<DbUser> query)
    {
        if (_filters.IncludeIds.Any())
        {
            query = query.Where(u => _filters.IncludeIds.Contains(u.Id));
        }

        if (_filters.ExcludeIds.Any())
        {
            query = query.Where(u => !_filters.ExcludeIds.Contains(u.Id));
        }

        if (!string.IsNullOrEmpty(_filters.TenantId))
        {
            query = query.Where(u => u.TenantId == _filters.TenantId);
        }

        if (!string.IsNullOrEmpty(_filters.SearchTerm))
        {
            var term = _filters.SearchTerm.ToUpper();

            query = query.Where(u =>
                u.Email.ToUpper().Contains(term) ||
                (
                    u.PhoneNumber != null &&
                    u.PhoneNumber.Contains(term)
                ) ||
                (
                    u.TelegramUsername != null &&
                    u.TelegramUsername.ToUpper().Contains(term)
                ) ||
                term.Split().Any(x => u.FirstName.ToUpper().Contains(x)) ||
                term.Split().Any(x => u.LastName.ToUpper().Contains(x))
            );
        }

        if (!string.IsNullOrEmpty(_filters.Email))
        {
            query = query.Where(u => u.Email.ToUpper() == _filters.Email.ToUpper());
        }

        if (!string.IsNullOrEmpty(_filters.PhoneNumber))
        {
            query = query.Where(u => u.PhoneNumber == _filters.PhoneNumber);
        }

        if (_filters.Roles.Any())
        {
            query = query.Where(u => u.Roles.Any(x => _filters.Roles.Contains(x.Role)));
        }

        return query;
    }

    private IQueryable<DbUser> PaginatedQuery(IQueryable<DbUser> query)
    {
        var (pageNumber, pageSize) = _pagination;

        return query
            .Skip((pageNumber - 1) * pageSize)
            .Take(pageSize);
    }
}
