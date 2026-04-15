using Domain.Authentication;

namespace Domain.Projects;

public interface IProjects
{
    IProjectSearchQuery Search(IUserIdentity requester);

    Task<IProject> Project(string projectId, IUserIdentity requester);

    Task<IProject> NewProject(NewProjectData newProject, IUserIdentity requester);

    Task Remove(string projectId, IUserIdentity requester);
}
