namespace Domain.Files;

public interface IFile
{
    string Name { get; }

    Stream Content();
}
