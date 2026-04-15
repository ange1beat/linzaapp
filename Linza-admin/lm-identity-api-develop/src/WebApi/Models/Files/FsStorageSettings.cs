using Provider.FileSystem;
using System.Text;
using WebApi.Exceptions;

namespace WebApi.Models.Files;

public class FsStorageSettings : IFsStorageSettings
{
    private const string BaseSection = "FileSystemStorage";

    private readonly IConfiguration _config;

    public FsStorageSettings(IConfiguration config)
    {
        _config = config;
    }

    public Uri FileUri(string scope, string name)
    {
        var storageBaseUrl = MandatoryValue<string>(
            "BaseUrl",
            "BaseUrl value is required"
        );

        var uriBuilder = new UriBuilder(storageBaseUrl);

        uriBuilder.Path = uriBuilder.Path.TrimEnd('/') + $"/{scope}/{name}";

        return uriBuilder.Uri;
    }

    public string Directory(string scope)
    {
        var baseDirectory = MandatoryValue<string>(
            "Directory",
            "Directory value is required"
        );
        var folder = new JenkinsHash(Encoding.UTF8.GetBytes(scope)).ToString();

        return $"{baseDirectory}/{folder}";
    }

    private T MandatoryValue<T>(string name, string errorMsg)
    {
        return _config.GetValue<T>($"{BaseSection}:{name}")
            ?? throw new AppConfigurationException(errorMsg);
    }
}
