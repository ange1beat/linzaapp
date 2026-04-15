namespace Domain.Search;

public record Pagination(int PageNumber, int PageSize)
{
    public Pagination() : this(1, int.MaxValue)
    {
    }
}
