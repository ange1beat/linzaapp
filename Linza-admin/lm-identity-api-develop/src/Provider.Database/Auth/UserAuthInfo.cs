using Domain.Media;
using Provider.Database.Users;

namespace Provider.Database.Auth;

internal sealed class UserAuthInfo : IWritable
{
    private readonly DbUser _user;

    public UserAuthInfo(DbUser user)
    {
        _user = user;
    }

    public void Write(IMedia media)
    {
        media.Write("Id", _user.Id);
        media.Write("Email", _user.Email);

        if (_user.PhoneNumber is not null)
        {
            media.Write("PhoneNumber", _user.PhoneNumber);
        }
    }
}
