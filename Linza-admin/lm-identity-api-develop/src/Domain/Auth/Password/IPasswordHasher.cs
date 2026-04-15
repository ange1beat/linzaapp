namespace Domain.Auth.Password;

public interface IPasswordHasher
{
    public string Hash(string password);

    public bool Match(string password, string passwordHash);
}
