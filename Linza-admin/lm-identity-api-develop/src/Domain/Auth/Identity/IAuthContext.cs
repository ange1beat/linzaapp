namespace Domain.Auth.Identity;

public interface IAuthContext
{
    IUserIdentity LoggedInIdentity();
}
