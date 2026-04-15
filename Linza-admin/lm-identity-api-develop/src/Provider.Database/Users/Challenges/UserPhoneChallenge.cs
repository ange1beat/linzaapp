using Domain.Auth.Exceptions;
using Domain.Auth.Identity;
using Domain.Auth.Tokens;
using Domain.Cellular;
using Domain.Messages;
using Domain.Users.Challenges;
using Domain.Users.Exceptions;
using System.Globalization;

namespace Provider.Database.Users.Challenges;

public class UserPhoneChallenge : IUserPhoneChallenge
{
    private const string RecipientPropKey = "Recipient";
    private const string CodeMsgKey = "${CODE}";

    private const VerificationScope Scope = VerificationScope.PhoneChange;

    private readonly IUserSettings _settings;
    private readonly IAuthContext _authCtx;
    private readonly IVerificationTokens _tokens;
    private readonly IMessageTemplates _messages;
    private readonly ICellularClient _cellularClient;

    public UserPhoneChallenge(
        IUserSettings settings,
        IAuthContext authCtx,
        IVerificationTokens tokens,
        IMessageTemplates messages,
        ICellularClient cellularClient)
    {
        _settings = settings;
        _authCtx = authCtx;
        _tokens = tokens;
        _messages = messages;
        _cellularClient = cellularClient;
    }

    public async Task SendSms(string phoneNumber, CultureInfo culture)
    {
        IUserIdentity identity = _authCtx.LoggedInIdentity();

        await CheckLimits(identity.UserId);

        string verificationCode = await _tokens.CreateToken(
            identity.UserId,
            Scope,
            _settings.OtpTokenTtl,
            new Dictionary<string, string>
            {
                { RecipientPropKey, phoneNumber }
            }
        );

        IMessageTemplate message = await _messages.Template(
            MessageType.PhoneChangeOtpSms,
            culture
        );

        // Move sms sending to background process
        await _cellularClient.Send(new SmsMessage(
            phoneNumber,
            message.Body(
                new MessageParam(CodeMsgKey, verificationCode)
            )
        ));
    }

    public async Task Verify(string phoneNumber, string passcode)
    {
        IUserIdentity identity = _authCtx.LoggedInIdentity();

        IVerificationToken? token = await _tokens.Token(identity.UserId, Scope);

        if (token is null)
        {
            throw new AccessDeniedException();
        }

        token.Properties.TryGetValue(RecipientPropKey, out var recipient);
        if (recipient is null || recipient != phoneNumber)
        {
            throw new AccessDeniedException();
        }

        await token.Use(passcode);
    }

    private async Task CheckLimits(string userId)
    {
        IVerificationToken? activeToken = await _tokens.Token(userId, Scope);

        if (activeToken is not null &&
            DateTime.UtcNow < activeToken.CreatedAt + _settings.SmsInterval)
        {
            throw new RetryLimitExceededException(
                activeToken.CreatedAt + _settings.SmsInterval
            );
        }
    }
}
