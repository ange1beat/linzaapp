using Domain.Authentication;
using Domain.Projects.Exceptions;
using Domain.Projects.Membership;
using Domain.Projects.Rules;
using Domain.Users;
using Microsoft.EntityFrameworkCore;
using Provider.Database.Context;
using Provider.Database.Projects.DbModels;

namespace Provider.Database.Projects.Membership;

public class ProjectsMembership : IProjectsMembership
{
    private readonly DatabaseContext _dbCtx;

    public ProjectsMembership(DatabaseContext dbCtx)
    {
        _dbCtx = dbCtx;
    }

    public async Task<IEnumerable<string>> ProjectIds(IUserIdentity requester)
    {
        var projectIds = await new DbProjectSearch(_dbCtx, requester)
            .PreparedQuery()
            .Select(p => p.Id)
            .ToListAsync();

        return projectIds;
    }

    public async Task<IEnumerable<string>> ProjectIds(IUser user, IUserIdentity requester)
    {
        new UserCanAccessUsersRule(requester, user).Enforce();

        var query = new DbProjectSearch(_dbCtx, requester).PreparedQuery();

        if (!user.IsSupervisor())
        {
            query = query.Where(p => p.Members.Any(m => m.UserId == user.Id));
        }

        IEnumerable<string> projectIds = await query.Select(p => p.Id).ToListAsync();

        return projectIds;
    }

    public async Task Assign(
        IUser user,
        IEnumerable<string> projectIds,
        IUserIdentity requester)
    {
        new UserCanAccessUsersRule(requester, user).Enforce();

        projectIds = projectIds.ToHashSet();

        if (!projectIds.Any()) return;

        var projects = await new DbProjectSearch(_dbCtx, requester)
            .PreparedQuery()
            .Where(p => projectIds.Contains(p.Id))
            .Select(p => new
            {
                p.Id,
                MemberIds = p.Members.Select(m => m.UserId)
            })
            .ToListAsync();

        var unknownProjectIds = projectIds.Except(projects.Select(p => p.Id)).ToList();
        if (unknownProjectIds.Count != 0)
        {
            throw new ProjectsNotFoundException(unknownProjectIds);
        }

        var assignedProjectIds = projects
            .Where(p => p.MemberIds.Any(mId => mId == user.Id))
            .Select(p => p.Id)
            .ToList();

        _dbCtx.AddRange(
            projectIds.Except(assignedProjectIds).Select(pId => new DbProjectMember
            {
                UserId = user.Id,
                ProjectId = pId,
                CreatedBy = requester.UserId
            })
        );

        await _dbCtx.SaveChangesAsync();
    }

    public async Task Remove(
        IUser user,
        IEnumerable<string> projectIds,
        IUserIdentity requester)
    {
        new UserCanAccessUsersRule(requester, user).Enforce();

        projectIds = projectIds.ToHashSet();

        if (!projectIds.Any()) return;

        await _dbCtx.Set<DbProjectMember>()
            .Include(pm => pm.Project)
            .Where(pm =>
                projectIds.Contains(pm.ProjectId) &&
                pm.UserId == user.Id &&
                pm.Project.TenantId == requester.TenantId
            )
            .ExecuteDeleteAsync();
    }

    public Task Remove(IUser user, IUserIdentity requester)
    {
        new UserCanAccessUsersRule(requester, user).Enforce();

        return _dbCtx.Set<DbProjectMember>()
            .Include(pm => pm.Project)
            .Where(pm =>
                pm.UserId == user.Id &&
                pm.Project.TenantId == requester.TenantId
            )
            .ExecuteDeleteAsync();
    }
}
