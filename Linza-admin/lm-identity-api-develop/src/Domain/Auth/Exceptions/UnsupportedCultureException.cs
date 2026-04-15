using System.Globalization;

namespace Domain.Auth.Exceptions;

public class UnsupportedCultureException : Exception
{
    private const string ErrorMsg = "Unsupported culture - '{0}'";

    public UnsupportedCultureException(CultureInfo culture) : this(culture.Name)
    {
    }

    public UnsupportedCultureException(string culture) : base(
        string.Format(CultureInfo.InvariantCulture, ErrorMsg, culture))
    {
    }
}
