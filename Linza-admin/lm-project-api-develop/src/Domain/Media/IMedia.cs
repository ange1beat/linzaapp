namespace Domain.Media;

public interface IMedia
{
    void Write<T>(string name, T value);
}
