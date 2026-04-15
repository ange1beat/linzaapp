using Domain.Auth;
using Domain.Auth.Exceptions;
using Domain.Auth.Factors;
using Domain.Auth.Tokens;
using Domain.Cellular;
using Domain.Email;
using Domain.Messages;
using Microsoft.EntityFrameworkCore;
using Newtonsoft.Json;
using Provider.Database.Auth.Tokens;
using Provider.Database.Context;
using Provider.Database.Tokens;
using Provider.Database.Users;
using System.Globalization;

namespace Provider.Database.Auth.Factors;

public class OtpAuthFactor : IOtpAuthFactor
{
    private const string RecipientPropKey = "Recipient";
    private const string DateMsgKey = "${DATE}";
    private const string CodeMsgKey = "${CODE}";

    private readonly IdentityDbContext _dbCtx;
    private readonly IAuthSettings _settings;
    private readonly IVerificationTokens _verificationTokens;
    private readonly IMessageTemplates _messages;
    private readonly IEmailClient _emailClient;
    private readonly ICellularClient _cellularClient;

    public OtpAuthFactor(
        IdentityDbContext dbCtx,
        IAuthSettings settings,
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

    public async Task ChallengeByEmail(string stateToken, CultureInfo culture)
    {
        DbUserToken authStateToken = await AuthStateToken(stateToken);

        var email = authStateToken.User.Email;

        string verificationCode = await _verificationTokens.CreateToken(
            authStateToken.UserId,
            VerificationScope.Mfa,
            _settings.OtpTokenTtl,
            new Dictionary<string, string> { { RecipientPropKey, email } }
        );

        IMessageTemplate message = await _messages.Template(
            MessageType.MfaOtpEmail,
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

    public async Task ChallengeBySms(string stateToken, CultureInfo culture)
    {
        DbUserToken authStateToken = await AuthStateToken(stateToken);

        var phoneNumber = authStateToken.User.PhoneNumber;

        if (phoneNumber is null)
        {
            throw new AccessDeniedException();
        }

        string verificationCode = await _verificationTokens.CreateToken(
            authStateToken.UserId,
            VerificationScope.Mfa,
            _settings.OtpTokenTtl,
            new Dictionary<string, string> { { RecipientPropKey, phoneNumber } }
        );

        IMessageTemplate message = await _messages.Template(
            MessageType.MfaOtpSms,
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

    public async Task<IAuthState> Verify(string stateToken, string passcode)
    {
        DbUserToken authStateToken = await AuthStateToken(stateToken);

        await VerifyOtp(authStateToken.User, passcode);

        var authData = JsonConvert.DeserializeObject<AuthTokenData>(authStateToken.Data!)!;
        authData.FactorsVerified.Add(FactorType.Otp);

        authStateToken.Data = JsonConvert.SerializeObject(authData);
        authStateToken.ExpiresAt = DateTime.UtcNow.Add(_settings.StateTokenTtl);

        _dbCtx.Update(authStateToken);

        await _dbCtx.SaveChangesAsync();

        return new AuthState(authStateToken);
    }

    private async Task<DbUserToken> AuthStateToken(string id)
    {
        var dbStateToken = await _dbCtx.Set<DbUserToken>()
            .Include(t => t.User)
            .Where(t =>
                t.Id == id &&
                t.Type == TokenType.Authentication &&
                t.ExpiresAt >= DateTime.UtcNow
            )
            .SingleOrDefaultAsync();

        if (dbStateToken is null)
        {
            throw new AccessDeniedException();
        }

        return dbStateToken;
    }

    private async Task VerifyOtp(DbUser user, string passcode)
    {
        IVerificationToken? otpToken = await _verificationTokens.Token(
            user.Id,
            VerificationScope.Mfa
        );

        if (otpToken is null)
        {
            throw new UnauthorizedException();
        }

        otpToken.Properties.TryGetValue(RecipientPropKey, out var recipient);
        if (recipient != user.Email && recipient != user.PhoneNumber)
        {
            throw new UnauthorizedException();
        }

        try
        {
            await otpToken.Use(passcode);
        }
        catch (AccessDeniedException)
        {
            throw new UnauthorizedException();
        }
    }
}
