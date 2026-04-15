using Domain.Authentication;

namespace Domain.Exceptions;

public class AccessDeniedException : Exception
{
    public IUserIdentity UserIdentity { get; }

    public AccessDeniedException(IUserIdentity userIdentity, string message)
        : base($"Access denied [User ID = {userIdentity.UserId}]: {message}")
    {
        UserIdentity = userIdentity;
    }
}
