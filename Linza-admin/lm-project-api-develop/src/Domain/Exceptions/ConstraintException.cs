namespace Domain.Exceptions;

public class ConstraintException : Exception
{
    public ConstraintException(string message) : base(message)
    {
    }

    public ConstraintException(string message, Exception innerException)
        : base(message, innerException)
    {
    }
}
