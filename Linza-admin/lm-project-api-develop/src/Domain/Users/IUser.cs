namespace Domain.Users;

public interface IUser
{
    string Id { get; }

    string TenantId { get; }

    bool IsSupervisor();
}
