namespace WebApi.Models.Responses.Auth;

public class PasswordRecoveryTokenResponse
{
    public string RecoveryToken { get; }

    public PasswordRecoveryTokenResponse(string recoveryToken)
    {
        RecoveryToken = recoveryToken;
    }
}
