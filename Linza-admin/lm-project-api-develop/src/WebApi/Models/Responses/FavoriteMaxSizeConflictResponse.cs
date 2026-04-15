namespace WebApi.Models.Responses;

public class FavoriteMaxSizeConflictResponse : ConflictResponse
{
    public override string Code => "favorites_max_size_limit";

    public override string Message => $"Favorites size limit exceeded. Max size = {_maxSizeLimit}";

    private readonly int _maxSizeLimit;

    public FavoriteMaxSizeConflictResponse(int maxSizeLimit)
    {
        _maxSizeLimit = maxSizeLimit;
    }
}
