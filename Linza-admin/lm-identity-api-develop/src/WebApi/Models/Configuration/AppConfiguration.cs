using WebApi.Exceptions;

namespace WebApi.Models.Configuration;

public class AppConfiguration
{
    private readonly IConfiguration _config;
    private readonly string _basePath;

    public AppConfiguration(IConfiguration config) : this(config, string.Empty)
    {
    }

    public AppConfiguration(IConfiguration config, string basePath)
    {
        _config = config;
        _basePath = basePath;
    }

    public T? Value<T>(string path)
    {
        var section = _config.GetSection($"{_basePath}:{path}");

        return section.Get<T>();
    }

    public T MandatoryValue<T>(string path)
    {
        var sectionKey = $"{_basePath}:{path}";
        var section = _config.GetSection($"{_basePath}:{path}");

        if (section.Exists())
        {
            return section.Get<T>() ?? throw new AppConfigurationException(
                $"Section {sectionKey} has invalid value"
            );
        }

        throw new AppConfigurationException(
            $"{sectionKey} value is required"
        );
    }
}
