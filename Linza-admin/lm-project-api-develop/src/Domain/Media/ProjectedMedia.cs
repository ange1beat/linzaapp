namespace Domain.Media;

public class ProjectedMedia : IMedia
{
    private readonly IMedia _origin;
    private readonly IEnumerable<string> _projection;

    public ProjectedMedia(IMedia origin, IEnumerable<string> projection)
    {
        _origin = origin;
        _projection = projection;
    }

    public void Write<T>(string name, T value)
    {
        if (_projection.Contains(name))
        {
            _origin.Write(name, value);
        }
    }
}
