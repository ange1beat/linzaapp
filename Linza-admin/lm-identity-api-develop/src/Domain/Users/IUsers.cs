namespace Domain.Users;

public interface IUsers
{
    IUserSearchQuery Search();

    Task<IUser> User(string userId);

    Task<IUser> NewUser(
        string invitationId,
        string firstName,
        string lastName,
        string password
    );

    Task Remove(string userId);
}
