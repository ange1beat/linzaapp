using System.Globalization;

namespace WebApi.Exceptions;

public class AppConfigurationException : Exception
{
    private const string ErrorMsgTemplate = "Configuration error: {0}";

    public AppConfigurationException(string cause) : base(
        string.Format(CultureInfo.InvariantCulture, ErrorMsgTemplate, cause))
    {
    }
}
