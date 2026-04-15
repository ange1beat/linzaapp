namespace Domain.Email;

public interface IEmailClient
{
    Task Send(EmailMessage message);
}
