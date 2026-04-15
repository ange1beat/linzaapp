using Provider.FileSystem.Files;
using System.Text;
using WebApi.Models.Settings;

namespace WebApi.Models.Files;

public class FsStorageSettings : ConfigSettingsBase, IFsStorageSettings
{
    private const string Section = "FileSystemStorage";

    public FsStorageSettings(IConfiguration config) : base(config, Section)
    {
    }

    public Uri FileUri(string scope, string name)
    {
        var storageBaseUrl = MandatoryValue<string>("BaseUrl");

        var uriBuilder = new UriBuilder(storageBaseUrl);

        uriBuilder.Path = uriBuilder.Path.TrimEnd('/') + $"/{scope}/{name}";

        return uriBuilder.Uri;
    }

    public string Directory(string scope)
    {
        var baseDirectory = MandatoryValue<string>("Directory");
        var folder = new JenkinsHash(Encoding.UTF8.GetBytes(scope)).ToString();

        return $"{baseDirectory}/{folder}";
    }
}
