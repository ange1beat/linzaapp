namespace Domain.Auth.Tokens;

public enum VerificationScope
{
    Mfa,
    PasswordRecovery,
    EmailChange,
    PhoneChange
}
