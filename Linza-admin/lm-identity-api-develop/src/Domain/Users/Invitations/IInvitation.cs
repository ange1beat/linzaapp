using Domain.Media;

namespace Domain.Users.Invitations;

public interface IInvitation : IWritable
{
    string Id { get; }
}
