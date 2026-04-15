namespace WebApi.Models.Responses;

public class ConflictResponse
{
    public virtual string Code { get; set; } = null!;

    public virtual string Message { get; set; } = null!;
}
