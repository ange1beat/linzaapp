using Domain.Media;
using Domain.Users.Invitations;

namespace Provider.Database.Users.Invitations;

internal sealed class Invitation : IInvitation
{
    public string Id => _entity.Id;

    private readonly DbInvitation _entity;

    public Invitation(DbInvitation entity)
    {
        _entity = entity;
    }

    public void Write(IMedia media)
    {
        media.Write("Id", _entity.Id);
        media.Write("TenantId", _entity.TenantId);
        media.Write("UserEmail", _entity.UserEmail);
        media.Write("UserRole", _entity.UserRole);
        media.Write("CreatedBy", _entity.CreatedBy);
        media.Write("CreatedAt", _entity.CreatedAt);
        media.Write("ExpiresAt", _entity.ExpiresAt);
    }
}
