using Domain.Auth.Recovery;
using Domain.Auth.Tokens;
using Domain.Cellular;
using Domain.Email;
using Domain.Messages;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Provider.Database.Context;
using Provider.Database.Messages;
using Provider.Database.Users;
using System.Globalization;

namespace Provider.Database.Auth.Recovery;

public class PasswordRecoveryCodes : IPasswordRecoveryCodes
{
    private const string RecipientPropKey = "Recipient";
    private const string DateMsgKey = "${DATE}";
    private const string CodeMsgKey = "${CODE}";

    private readonly IdentityDbContext _dbCtx;
    private readonly IRecoverySettings _settings;
    private readonly IVerificationTokens _verificationTokens;
    private readonly IMessageTemplates _messages;
    private readonly IEmailClient _emailClient;
    private readonly ICellularClient _cellularClient;

    public PasswordRecoveryCodes(
        IdentityDbContext dbCtx,
        IRecoverySettings settings,
        IVerificationTokens verificationTokens,
        IMessageTemplates messages,
        IEmailClient emailClient,
        ICellularClient cellularClient)
    {
        _dbCtx = dbCtx;
        _settings = settings;
        _verificationTokens = verificationTokens;
        _messages = messages;
        _emailClient = emailClient;
        _cellularClient = cellularClient;
    }

    public async Task SendEmail(string email, CultureInfo culture)
    {
        if (email.IsNullOrEmpty())
        {
            throw new ArgumentException("Invalid email", nameof(email));
        }

        var user = await _dbCtx.Set<DbUser>()
            .Where(u => u.Email.ToUpper() == email.ToUpper())
            .SingleOrDefaultAsync();

        if (user is null)
        {
            return;
        }

        await SendEmail(user, culture);
    }

    public async Task SendSms(string phoneNumber, CultureInfo culture)
    {
        if (phoneNumber.IsNullOrEmpty())
        {
            throw new ArgumentException("Invalid phone number", nameof(phoneNumber));
        }

        var user = await _dbCtx.Set<DbUser>()
            .Where(u =>
                u.PhoneNumber != null &&
                u.PhoneNumber == phoneNumber
            )
            .SingleOrDefaultAsync();

        if (user is null)
        {
            return;
        }

        await SendSms(user, culture);
    }

    private async Task SendEmail(DbUser user, CultureInfo culture)
    {
        string recoveryCode = await _verificationTokens.CreateToken(
            user.Id,
            VerificationScope.PasswordRecovery,
            _settings.OtpTokenTtl,
            new Dictionary<string, string>
            {
                { RecipientPropKey, user.Email }
            }
        );

        IMessageTemplate message = await _messages.Template(
            MessageType.PasswordRecoveryOtpEmail,
            culture
        );

        EmailMessage emailMessage = new EmailMessage(
            user.Email,
            message.Subject(
                new MessageParam(DateMsgKey, DateTime.UtcNow.ToString(culture))
            ),
            message.Body(
                new MessageParam(CodeMsgKey, recoveryCode)
            )
        );

        // Move email sending to background process
        await _emailClient.Send(emailMessage);
    }

    private async Task SendSms(DbUser user, CultureInfo culture)
    {
        string recoveryCode = await _verificationTokens.CreateToken(
            user.Id,
            VerificationScope.PasswordRecovery,
            _settings.OtpTokenTtl,
            new Dictionary<string, string>
            {
                { RecipientPropKey, user.PhoneNumber! }
            }
        );

        IMessageTemplate message = await _messages.Template(
            MessageType.PasswordRecoveryOtpSms,
            culture
        );

        SmsMessage smsMessage = new SmsMessage(
            user.PhoneNumber!,
            message.Body(
                new MessageParam(CodeMsgKey, recoveryCode)
            )
        );

        // Move sms sending to background process
        await _cellularClient.Send(smsMessage);
    }
}
