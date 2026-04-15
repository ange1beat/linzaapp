namespace Domain.Exceptions;

public class ConcurrencyException : Exception
{
    private const string MessageError = "Concurrency error";

    public ConcurrencyException() : base(MessageError)
    {
    }

    public ConcurrencyException(Exception? innerException) : base(MessageError, innerException)
    {
    }
}
