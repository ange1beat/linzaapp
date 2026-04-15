using System.Globalization;

namespace Domain.Projects.Exceptions;

public class ProjectNotFoundException : Exception
{
    private const string MessageTemplate = "Project - '{0}' is not found!";

    public ProjectNotFoundException(string projectId) : base(
        string.Format(CultureInfo.InvariantCulture, MessageTemplate, projectId))
    {
    }
}
