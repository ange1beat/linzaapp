namespace Domain.Cellular;

public interface ISmsNadoClientSettings
{
    Uri BaseUrl { get; }

    string User { get; }

    string Password { get; }

    string Sender { get; }
}
