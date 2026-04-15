using Domain.Authentication;
using Domain.Projects;
using Domain.Projects.Rules;
using Domain.Users;
using Provider.Database.Context;
using Provider.Database.Projects.DbModels;
using System.Collections;

namespace Provider.Database.Projects;

internal sealed class ProjectMembers : IProjectMembers
{
    private readonly DbProject _entity;
    private readonly DatabaseContext _dbCtx;
    private readonly IUserIdentity _requester;

    public ProjectMembers(DbProject entity, DatabaseContext dbCtx, IUserIdentity requester)
    {
        _entity = entity;
        _dbCtx = dbCtx;
        _requester = requester;
    }

    public IEnumerator<string> GetEnumerator()
    {
        return _entity.Members.Select(m => m.UserId).GetEnumerator();
    }

    public Task Add(IEnumerable<IUser> users)
    {
        new UserCanUpdateProjectRule(_requester).Enforce();

        users = users.ToList();
        new UserCanAccessUsersRule(_requester, users).Enforce();

        var existingUserIds = _entity.Members.Select(m => m.UserId).ToHashSet();
        foreach (var user in users)
        {
            if (!existingUserIds.Contains(user.Id))
            {
                _entity.Members.Add(new DbProjectMember
                {
                    UserId = user.Id,
                    ProjectId = _entity.Id,
                    CreatedBy = _requester.UserId
                });
            }
        }

        _dbCtx.Update(_entity);

        return _dbCtx.SaveChangesAsync();
    }

    public Task Remove(string userId)
    {
        new UserCanUpdateProjectRule(_requester).Enforce();

        _entity.Members.RemoveAll(m => m.UserId == userId);

        _dbCtx.Update(_entity);

        return _dbCtx.SaveChangesAsync();
    }

    IEnumerator IEnumerable.GetEnumerator()
    {
        return GetEnumerator();
    }
}
