using Domain.Email;
using MailKit.Net.Smtp;
using MimeKit;
using MimeKit.Text;

namespace Provider.Email;

public class EmailClient : IEmailClient
{
    private readonly ISmtpSettings _settings;

    public EmailClient(ISmtpSettings settings)
    {
        _settings = settings;
    }

    public async Task Send(EmailMessage message)
    {
        using var emailMessage = new MimeMessage();

        emailMessage.From.Add(new MailboxAddress(_settings.NameFrom, _settings.AddressFrom));
        emailMessage.To.Add(new MailboxAddress(string.Empty, message.To));
        emailMessage.Subject = message.Subject;
        emailMessage.Body = new TextPart(TextFormat.Html)
        {
            Text = message.Body
        };

        using var smtpClient = new SmtpClient();

        await smtpClient.ConnectAsync(_settings.Host, _settings.Port, true);
        await smtpClient.AuthenticateAsync(_settings.Login, _settings.Password);
        await smtpClient.SendAsync(emailMessage);

        await smtpClient.DisconnectAsync(true);
    }
}
