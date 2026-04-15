using Domain.Auth.Identity;
using Domain.Users;
using System.ComponentModel.DataAnnotations;

namespace WebApi.Models.Requests.Users;

public class ChangeUserRolesRequest
{
    [Required]
    public bool IsSupervisor { get; set; } = default!;

    public Task ChangeRoles(IUser user)
    {
        var roles = new List<Role> { Role.User };

        if (IsSupervisor)
        {
            roles.Add(Role.Supervisor);
        }

        return user.ChangeRoles(roles);
    }
}
