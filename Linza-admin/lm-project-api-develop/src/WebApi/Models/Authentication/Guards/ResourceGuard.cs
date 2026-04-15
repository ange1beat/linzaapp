using System.Collections.Specialized;
using System.Security.Cryptography;
using System.Web;

namespace WebApi.Models.Authentication.Guards;

public class ResourceGuard : IResourceGuard
{
    private const string SignatureParamName = "sig";
    private const int Pbkdf2Iterations = 10_000;
    private const int Pbkdf2SaltSize = 0;

    private readonly IResourceGuardSettings _settings;

    public ResourceGuard(IResourceGuardSettings settings)
    {
        _settings = settings;
    }

    public Uri SignedUrl(Uri url)
    {
        var urlBuilder = new UriBuilder(url);

        NameValueCollection urlQuery = HttpUtility.ParseQueryString(urlBuilder.Query);
        urlQuery[SignatureParamName] = Signature();

        urlBuilder.Query = urlQuery.ToString();

        return urlBuilder.Uri;
    }

    public Uri SignedUrl(string url)
    {
        return SignedUrl(new Uri(url));
    }

    public bool IsUrlValid(Uri url)
    {
        NameValueCollection urlQuery = HttpUtility.ParseQueryString(url.Query);
        string? signature = urlQuery.Get(SignatureParamName);

        return signature is not null && IsSignatureValid(signature);
    }

    public bool IsUrlValid(string url)
    {
        return IsUrlValid(new Uri(url));
    }

    private string Signature()
    {
        using var pbkdf2 = new Rfc2898DeriveBytes(
            password: _settings.SecretKey,
            saltSize: Pbkdf2SaltSize,
            iterations: Pbkdf2Iterations,
            hashAlgorithm: HashAlgorithmName.SHA256
        );

        return Convert.ToBase64String(pbkdf2.GetBytes(32));
    }

    private bool IsSignatureValid(string signature)
    {
        using var pbkdf2 = new Rfc2898DeriveBytes(
            password: _settings.SecretKey,
            saltSize: Pbkdf2SaltSize,
            iterations: Pbkdf2Iterations,
            hashAlgorithm: HashAlgorithmName.SHA256
        );

        byte[] storedHash = pbkdf2.GetBytes(32); // 32 bytes for a 256-bit key
        byte[] inputHash = Convert.FromBase64String(signature);

        // Compare the derived hash with the stored hash
        return storedHash.SequenceEqual(inputHash);
    }
}
