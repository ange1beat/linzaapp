using System.Globalization;

namespace Domain.Files.Exceptions;

public class FileNotFoundException : Exception
{
    private const string MessageTemplate = "File - [scope:'{1}', name:'{0}'] is not found!";

    public FileNotFoundException(string scope, string name, Exception? cause = null) : base(
        string.Format(CultureInfo.InvariantCulture, MessageTemplate, scope, name),
        cause)
    {
    }
}
