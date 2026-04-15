using System.Globalization;

namespace Domain.Projects.Exceptions;

public class ProjectsNotFoundException : Exception
{
    private const string MessageTemplate = "Projects [{0}] are not found";

    public readonly IEnumerable<string> ProjectIds;

    public ProjectsNotFoundException(IReadOnlyCollection<string> projectIds) : base(
        string.Format(
            CultureInfo.InvariantCulture,
            MessageTemplate,
            string.Join(',', projectIds)))
    {
        ProjectIds = projectIds;
    }
}
