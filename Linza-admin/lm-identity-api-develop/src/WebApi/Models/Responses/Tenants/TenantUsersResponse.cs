using Domain.Auth.Identity;
using Domain.Media;
using Domain.Users;

namespace WebApi.Models.Responses.Tenants;

public class TenantUsersResponse
{
    public IEnumerable<TenantUserDto> Users => _users.Select(user =>
    {
        var dto = new TenantUserDto();
        user.Write(dto);

        return dto;
    });

    private readonly IEnumerable<IUser> _users;

    public TenantUsersResponse(IEnumerable<IUser> users)
    {
        _users = users;
    }
}

public class TenantUserDto : ReflectedMedia
{
    public string Id { get; set; } = default!;

    public IEnumerable<Role> Roles { get; set; } = default!;
}
