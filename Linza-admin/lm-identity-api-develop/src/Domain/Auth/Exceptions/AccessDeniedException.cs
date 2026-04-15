namespace Domain.Auth.Exceptions;

public class AccessDeniedException : Exception
{
    public AccessDeniedException() : base("Access denied")
    {
    }
}
