using Domain.Auth.Exceptions;
using Domain.Auth.Identity;
using Domain.Auth.Tokens;
using Domain.Email;
using Domain.Messages;
using Domain.Users.Challenges;
using Domain.Users.Exceptions;
using System.Globalization;

namespace Provider.Database.Users.Challenges;

public class UserEmailChallenge : IUserEmailChallenge
{
    private const string RecipientPropKey = "Recipient";
    private const string DateMsgKey = "${DATE}";
    private const string CodeMsgKey = "${CODE}";

    private const VerificationScope Scope = VerificationScope.EmailChange;

    private readonly IUserSettings _settings;
    private readonly IAuthContext _authCtx;
    private readonly IVerificationTokens _tokens;
    private readonly IMessageTemplates _messages;
    private readonly IEmailClient _emailClient;

    public UserEmailChallenge(
        IUserSettings settings,
        IAuthContext authCtx,
        IVerificationTokens tokens,
        IMessageTemplates messages,
        IEmailClient emailClient)
    {
        _settings = settings;
        _authCtx = authCtx;
        _tokens = tokens;
        _messages = messages;
        _emailClient = emailClient;
    }

    public async Task SendEmail(string email, CultureInfo culture)
    {
        IUserIdentity identity = _authCtx.LoggedInIdentity();

        await CheckLimits(identity.UserId);

        string verificationCode = await _tokens.CreateToken(
            identity.UserId,
            Scope,
            _settings.OtpTokenTtl,
            new Dictionary<string, string>
            {
                { RecipientPropKey, email }
            }
        );

        IMessageTemplate message = await _messages.Template(
            MessageType.EmailChangeOtpEmail,
            culture
        );

        // Move email sending to background process
        await _emailClient.Send(new EmailMessage(
            email,
            message.Subject(
                new MessageParam(DateMsgKey, DateTime.UtcNow.ToString(culture))
            ),
            message.Body(
                new MessageParam(CodeMsgKey, verificationCode)
            )
        ));
    }

    public async Task Verify(string email, string passcode)
    {
        IUserIdentity identity = _authCtx.LoggedInIdentity();

        IVerificationToken? token = await _tokens.Token(identity.UserId, Scope);

        if (token is null)
        {
            throw new AccessDeniedException();
        }

        token.Properties.TryGetValue(RecipientPropKey, out var recipient);
        if (recipient is null || recipient.ToUpper() != email.ToUpper())
        {
            throw new AccessDeniedException();
        }

        await token.Use(passcode);
    }

    private async Task CheckLimits(string userId)
    {
        IVerificationToken? activeToken = await _tokens.Token(userId, Scope);

        if (activeToken is not null &&
            DateTime.UtcNow < activeToken.CreatedAt + _settings.EmailInterval)
        {
            throw new RetryLimitExceededException(
                activeToken.CreatedAt + _settings.SmsInterval
            );
        }
    }
}
