namespace Domain.Auth;

public interface IBaseAuth
{
    Task<IAuthState> Authenticate(string login, string password);
}
