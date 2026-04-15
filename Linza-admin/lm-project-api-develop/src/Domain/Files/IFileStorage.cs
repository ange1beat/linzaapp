namespace Domain.Files;

public interface IFileStorage
{
    Uri FileUri(string scope, string filename);

    Task Upload(string scope, string filename, Stream fileContent);

    Task<IFile> File(string scope, string filename);

    Task Remove(string scope, string filename);
}
