namespace Domain.Projects.Exceptions;

public class SizeLimitExceededException : Exception
{
    public int MaxSize { get; }

    public SizeLimitExceededException(int maxSize)
        : base($"Size limit exceeded! Max size = {maxSize}")
    {
        MaxSize = maxSize;
    }
}
