namespace Domain.Auth.Tokens;

public interface IVerificationTokens
{
    Task<string> CreateToken(
        string userId,
        VerificationScope scope,
        TimeSpan lifeTime,
        IEnumerable<KeyValuePair<string, string>> properties
    );

    Task<IVerificationToken?> Token(string userId, VerificationScope scope);
}
