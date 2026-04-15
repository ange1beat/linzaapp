namespace Domain.Auth.Identity;

public interface IUserIdentity
{
    string UserId { get; }

    string TenantId { get; }

    bool IsInRole(Role role);
}
