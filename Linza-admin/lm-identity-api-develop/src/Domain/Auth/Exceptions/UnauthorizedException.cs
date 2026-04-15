namespace Domain.Auth.Exceptions;

public class UnauthorizedException : Exception
{
    public UnauthorizedException() : base("Unauthorized access")
    {
    }
}
