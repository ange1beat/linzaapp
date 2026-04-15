using System.Globalization;

namespace WebApi.Exceptions;

public class ConfigurationException : Exception
{
    private const string ErrorMsgTemplate = "Configuration error: {0}";

    public ConfigurationException(string cause) : base(
        string.Format(CultureInfo.InvariantCulture, ErrorMsgTemplate, cause))
    {
    }
}
