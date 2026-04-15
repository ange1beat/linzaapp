using Provider.Email;
using WebApi.Models.Configuration;

namespace WebApi.Models.Auth;

public class SmtpSettings : ISmtpSettings
{
    private const string BaseSection = "Smtp";

    public string Host => _appConfig.MandatoryValue<string>("Host");

    public int Port => _appConfig.MandatoryValue<int>("Port");

    public string Login => _appConfig.MandatoryValue<string>("Login");

    public string Password => _appConfig.MandatoryValue<string>("Password");

    public string NameFrom => _appConfig.MandatoryValue<string>("NameFrom");

    public string AddressFrom => _appConfig.MandatoryValue<string>("AddressFrom");

    private readonly AppConfiguration _appConfig;

    public SmtpSettings(IConfiguration config)
        : this(new AppConfiguration(config, BaseSection))
    {
    }

    private SmtpSettings(AppConfiguration appConfig)
    {
        _appConfig = appConfig;
    }
}
