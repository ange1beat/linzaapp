using Domain.Users;

namespace WebApi.Models.Responses.Users;

public class UserPagedListResponse
{
    public IEnumerable<UserResponse> Users => _users.Select(user =>
    {
        var response = new UserResponse();
        user.Write(response);

        return response;
    });

    public int Total { get; }

    private readonly IEnumerable<IUser> _users;

    public UserPagedListResponse(IEnumerable<IUser> users, int total)
    {
        _users = users;
        Total = total;
    }
}
