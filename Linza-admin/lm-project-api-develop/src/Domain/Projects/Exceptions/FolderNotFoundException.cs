using System.Globalization;

namespace Domain.Projects.Exceptions;

public class FolderNotFoundException : Exception
{
    private const string MessageTemplate = "Folder - '{0}' is not found!";

    public FolderNotFoundException(string folderId) : base(
        string.Format(CultureInfo.InvariantCulture, MessageTemplate, folderId))
    {
    }
}
