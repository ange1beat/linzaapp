namespace Domain.Authentication;

public interface IUserIdentity
{
    string UserId { get; }

    string TenantId { get; }

    string AccessToken();

    bool IsAdmin();

    bool IsSupervisor();
}
