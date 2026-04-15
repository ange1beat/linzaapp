namespace Provider.Email;

public interface ISmtpSettings
{
    public string Host { get; }

    public int Port { get; }

    public string Login { get; }

    public string Password { get; }

    public string NameFrom { get; }

    public string AddressFrom { get; }
}
