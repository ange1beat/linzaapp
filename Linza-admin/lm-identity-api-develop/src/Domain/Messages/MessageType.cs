namespace Domain.Messages;

public enum MessageType
{
    MfaOtpEmail,
    MfaOtpSms,
    PasswordRecoveryOtpEmail,
    PasswordRecoveryOtpSms,
    InvitationEmail,
    EmailChangeOtpEmail,
    PhoneChangeOtpSms
}
