namespace Domain.Auth.Recovery;

public interface IPasswordRecovery
{
    Task<string> RecoveryToken(string login, string recoveryCode);

    Task ResetPassword(string recoveryToken, string newPassword);
}
