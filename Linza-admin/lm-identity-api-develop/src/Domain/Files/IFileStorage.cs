namespace Domain.Files;

public interface IFileStorage
{
    Uri FileUri(string scope, string name);

    Task Upload(string scope, string name, Stream fileContent);

    Task<IFile> File(string scope, string name);

    Task Remove(string scope, params string[] names);
}
