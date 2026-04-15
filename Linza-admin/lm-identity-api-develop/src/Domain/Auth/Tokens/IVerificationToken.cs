namespace Domain.Auth.Tokens;

public interface IVerificationToken
{
    DateTime CreatedAt { get; }

    IReadOnlyDictionary<string, string> Properties { get; }

    Task Use(string passcode);
}
