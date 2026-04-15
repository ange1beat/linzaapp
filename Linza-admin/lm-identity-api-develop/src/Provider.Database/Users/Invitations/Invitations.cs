using Domain.Auth.Identity;
using Domain.Email;
using Domain.Guid;
using Domain.Messages;
using Domain.Users.Exceptions;
using Domain.Users.Invitations;
using Domain.Users.Rules;
using Microsoft.EntityFrameworkCore;
using Provider.Database.Context;
using System.Globalization;

namespace Provider.Database.Users.Invitations;

public class Invitations : IInvitations
{
    private const string DateMsgKey = "${DATE}";
    private const string RegistrationLinkMsgKey = "${LINK}";

    private readonly IAuthContext _authCtx;
    private readonly IdentityDbContext _dbCtx;
    private readonly IInvitationSettings _settings;
    private readonly IMessageTemplates _messages;
    private readonly IEmailClient _emailClient;

    public Invitations(
        IAuthContext authCtx,
        IdentityDbContext dbCtx,
        IInvitationSettings settings,
        IMessageTemplates messages,
        IEmailClient emailClient)
    {
        _authCtx = authCtx;
        _dbCtx = dbCtx;
        _settings = settings;
        _messages = messages;
        _emailClient = emailClient;
    }

    public async Task<IInvitation> NewInvitation(string email, CultureInfo culture)
    {
        IUserIdentity requester = _authCtx.LoggedInIdentity();

        new UserCanManageInvitationRule(requester).Enforce();

        if (await _dbCtx.Set<DbUser>()
                .AnyAsync(u => u.Email.ToUpper() == email.ToUpper()))
        {
            throw new EmailConflictException(email);
        }

        var invitation = new DbInvitation
        {
            Id = new ShortGuid(Guid.NewGuid()).ToString(),
            TenantId = requester.TenantId,
            UserEmail = email,
            UserRole = Role.User,
            CreatedBy = requester.UserId,
            ExpiresAt = DateTime.UtcNow.Add(_settings.InvitationTtl)
        };

        await SaveInvitation(invitation);
        await SendInvitation(invitation, culture);

        return new Invitation(invitation);
    }

    public async Task<IInvitation> Invitation(string invitationId)
    {
        var invitation = await _dbCtx.Set<DbInvitation>()
            .SingleOrDefaultAsync(inv => inv.Id == invitationId);

        if (invitation is null)
        {
            throw new InvitationNotFoundException(invitationId);
        }

        return new Invitation(invitation);
    }

    public Task Remove(string invitationId)
    {
        IUserIdentity requester = _authCtx.LoggedInIdentity();

        new UserCanManageInvitationRule(requester).Enforce();

        return _dbCtx.Set<DbInvitation>()
            .Where(inv =>
                inv.Id == invitationId &&
                inv.TenantId == requester.TenantId
            )
            .ExecuteDeleteAsync();
    }

    private async Task SaveInvitation(DbInvitation invitation)
    {
        // Retries operation if any issues with optimistic concurrency control
        int remainingRetryCount = 10;
        do
        {
            try
            {
                await using var transaction = _dbCtx.Transaction();

                await _dbCtx.Set<DbInvitation>()
                    .Where(inv =>
                        inv.UserEmail.ToUpper() == invitation.UserEmail.ToUpper() ||
                        // cleanup expired invitations can be moved to background process
                        //      to improve performance
                        inv.ExpiresAt < DateTime.UtcNow
                    )
                    .ExecuteDeleteAsync();

                _dbCtx.Add(invitation);

                await _dbCtx.SaveChangesAsync();

                await transaction.CommitAsync();

                return;
            }
            catch (DbUpdateException exc) when (
                exc is DbUpdateConcurrencyException ||
                _dbCtx.IsUniqueViolationError(exc, nameof(DbInvitation.UserEmail)))
            {
                remainingRetryCount--;
            }
        } while (remainingRetryCount > 0);
    }

    private async Task SendInvitation(DbInvitation invitation, CultureInfo culture)
    {
        IMessageTemplate message = await _messages.Template(
            MessageType.InvitationEmail,
            culture
        );

        Uri registrationLink = _settings.RegistrationLink(invitation.Id, culture);

        EmailMessage emailMessage = new EmailMessage(
            invitation.UserEmail,
            message.Subject(
                new MessageParam(DateMsgKey, DateTime.UtcNow.ToString(culture))
            ),
            message.Body(
                new MessageParam(RegistrationLinkMsgKey, registrationLink.ToString())
            )
        );

        // Move email sending to background process
        await _emailClient.Send(emailMessage);
    }
}
