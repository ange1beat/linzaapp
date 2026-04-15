using Domain.Auth;
using Microsoft.IdentityModel.Tokens;
using System.Security.Cryptography;
using System.Xml;
using WebApi.Exceptions;

namespace WebApi.Models.Auth;

public class JwtSettings : IJwtSettings
{
    private const string Section = "Authentication:JWT";

    public string Issuer => MandatoryValue<string>("Issuer");

    public string Audience => MandatoryValue<string>("Audience");

    public TimeSpan ExpirationTime =>
        XmlConvert.ToTimeSpan(MandatoryValue<string>("ExpirationTime"));

    private string PublicKey => MandatoryValue<string>("PublicKey");

    private string PrivateKey => MandatoryValue<string>("PrivateKey");

    private readonly IConfiguration _config;

    public JwtSettings(IConfiguration config)
    {
        _config = config;
    }

    public IEnumerable<SecurityKey> SigningKeys()
    {
        var rsaKey = RSA.Create();

        rsaKey.ImportFromPem(PublicKey);

        return new List<SecurityKey>
        {
            new RsaSecurityKey(rsaKey.ExportParameters(false))
        };
    }

    public SigningCredentials SigningCredentials()
    {
        var rsa = RSA.Create();
        rsa.ImportFromPem(PrivateKey);

        return new SigningCredentials(
            new RsaSecurityKey(rsa.ExportParameters(true)),
            SecurityAlgorithms.RsaSha256
        );
    }

    private T MandatoryValue<T>(string name)
    {
        var key = $"{Section}:{name}";

        return _config.GetValue<T>(key)
            ?? throw new AppConfigurationException($"{key} is required");
    }
}
