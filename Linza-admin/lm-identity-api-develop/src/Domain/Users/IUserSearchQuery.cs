using Domain.Search;

namespace Domain.Users;

public interface IUserSearchQuery
{
    IUserSearchQuery WithIds(params string[] ids);

    IUserSearchQuery WithoutIds(params string[] ids);

    IUserSearchQuery WithTenant(string tenantId);

    IUserSearchQuery WithSearchTerm(string name);

    IUserSearchQuery WithEmail(string email);

    IUserSearchQuery WithPhone(string phoneNumber);

    IUserSearchQuery WithPagination(Pagination pagination);

    Task<bool> Any();

    Task<IReadOnlyCollection<IUser>> Result();

    Task<int> Total();
}
