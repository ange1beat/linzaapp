using Domain.Exceptions;
using Domain.Users;

namespace Domain.Projects;

public record NewProjectData(
    string Name,
    IEnumerable<IUser> Members)
{
    public void Validate()
    {
        if (Name.Length == 0)
        {
            throw new ValidationException(nameof(Name), "Project name is required");
        }
    }
}
