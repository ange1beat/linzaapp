using Domain.Authentication;
using Domain.Exceptions;
using Domain.Files;
using Domain.Projects;
using Domain.Projects.Exceptions;
using Domain.Projects.Rules;
using Microsoft.EntityFrameworkCore;
using Provider.Database.Context;
using Provider.Database.Guid;
using Provider.Database.Projects.DbModels;

namespace Provider.Database.Projects;

public class Projects : IProjects
{
    private readonly DatabaseContext _dbCtx;
    private readonly IProjectSettings _settings;
    private readonly IFileStorage _files;

    public Projects(DatabaseContext dbCtx, IProjectSettings settings, IFileStorage files)
    {
        _dbCtx = dbCtx;
        _settings = settings;
        _files = files;
    }

    public IProjectSearchQuery Search(IUserIdentity requester)
    {
        return new ProjectSearchQuery(_dbCtx, _settings, _files, requester);
    }

    public async Task<IProject> Project(string projectId, IUserIdentity requester)
    {
        var dbProject = await new DbProjectSearch(_dbCtx, requester)
            .PreparedQuery()
            .Where(p => p.Id == projectId)
            .SingleOrDefaultAsync();

        if (dbProject is null)
        {
            throw new ProjectNotFoundException(projectId);
        }

        return new Project(dbProject, _dbCtx, _settings, _files, requester);
    }

    public async Task<IProject> NewProject(NewProjectData newProject, IUserIdentity requester)
    {
        new UserCanCreateProjectsRule(requester).Enforce();
        new UserCanAccessUsersRule(requester, newProject.Members).Enforce();

        await Validate(newProject, requester);

        var projectId = new ShortGuid(System.Guid.NewGuid()).ToString();

        var dbProject = new DbProject
        {
            Id = projectId,
            TenantId = requester.TenantId,
            Name = newProject.Name,
            CreatedBy = requester.UserId,
            UpdatedBy = requester.UserId,
            Members = newProject.Members
                .Select(pm => new DbProjectMember
                {
                    UserId = pm.Id,
                    ProjectId = projectId,
                    CreatedBy = requester.UserId
                })
                .ToList()
        };
        _dbCtx.Add(dbProject);

        await _dbCtx.SaveChangesAsync();

        return new Project(dbProject, _dbCtx, _settings, _files, requester);
    }

    public async Task Remove(string projectId, IUserIdentity requester)
    {
        new UserCanRemoveProjectsRule(requester).Enforce();

        var dbProject = await new DbProjectSearch(_dbCtx, requester)
            .PreparedQuery()
            .Where(p => p.Id == projectId)
            .SingleOrDefaultAsync();

        if (dbProject is null)
        {
            return;
        }

        var project = new Project(dbProject, _dbCtx, _settings, _files, requester);

        await project.Delete();
    }

    private async Task Validate(NewProjectData newProject, IUserIdentity requester)
    {
        newProject.Validate();

        if (await _dbCtx.Set<DbProject>().AnyAsync(p =>
                p.TenantId == requester.TenantId &&
                p.Name.ToUpper() == newProject.Name.ToUpper()))
        {
            throw new ConstraintException("Project name must be unique!");
        }
    }
}
