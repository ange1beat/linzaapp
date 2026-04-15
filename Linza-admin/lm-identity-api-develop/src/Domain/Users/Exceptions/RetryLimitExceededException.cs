namespace Domain.Users.Exceptions;

public class RetryLimitExceededException : Exception
{
    public DateTime RetryAfter { get; }

    public RetryLimitExceededException(DateTime retryAfter) : base("Retry limit exceeded")
    {
        RetryAfter = retryAfter;
    }
}
