using WebApi.Exceptions;

namespace WebApi.Models.Settings;

public abstract class ConfigSettingsBase
{
    protected readonly IConfiguration _config;
    protected readonly string _baseSectionName;

    protected ConfigSettingsBase(IConfiguration config, string baseSectionName)
    {
        _config = config;
        _baseSectionName = baseSectionName;
    }

    protected T MandatoryValue<T>(string name)
    {
        var sectionKey = $"{_baseSectionName}:{name}";
        var section = _config.GetSection($"{_baseSectionName}:{name}");

        if (section.Exists())
        {
            return section.Get<T>() ?? throw new ConfigurationException(
                $"Section {sectionKey} has invalid value"
            );
        }

        throw new ConfigurationException(
            $"{sectionKey} value is required"
        );
    }
}
